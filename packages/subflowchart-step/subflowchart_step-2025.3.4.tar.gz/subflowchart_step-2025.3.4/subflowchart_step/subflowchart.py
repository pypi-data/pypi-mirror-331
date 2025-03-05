# -*- coding: utf-8 -*-

"""Non-graphical part of the Subflowchart step in a SEAMM flowchart"""

import logging
from pathlib import Path
import pkg_resources
import pprint  # noqa: F401
import sys
import traceback

from loop_step import ContinueLoop, BreakLoop, SkipIteration
import subflowchart_step
import molsystem
import seamm
from seamm_util import ureg, Q_, getParser  # noqa: F401
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __

# In addition to the normal logger, two logger-like printing facilities are
# defined: "job" and "printer". "job" send output to the main job.out file for
# the job, and should be used very sparingly, typically to echo what this step
# will do in the initial summary of the job.
#
# "printer" sends output to the file "step.out" in this steps working
# directory, and is used for all normal output from this step.

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter("Subflowchart")

# Add this module's properties to the standard properties
path = Path(pkg_resources.resource_filename(__name__, "data/"))
csv_file = path / "properties.csv"
if path.exists():
    molsystem.add_properties_from_file(csv_file)


class Subflowchart(seamm.Node):
    """
    The non-graphical part of a Subflowchart step in a flowchart.

    Attributes
    ----------
    parser : configargparse.ArgParser
        The parser object.

    options : tuple
        It contains a two item tuple containing the populated namespace and the
        list of remaining argument strings.

    subflowchart : seamm.Flowchart
        A SEAMM Flowchart object that represents a subflowchart, if needed.

    parameters : SubflowchartParameters
        The control parameters for Subflowchart.

    See Also
    --------
    TkSubflowchart,
    Subflowchart, SubflowchartParameters
    """

    def __init__(
        self,
        flowchart=None,
        title="Subflowchart",
        namespace="org.molssi.seamm",
        extension=None,
        logger=logger,
    ):
        """A step for Subflowchart in a SEAMM flowchart.

        You may wish to change the title above, which is the string displayed
        in the box representing the step in the flowchart.

        Parameters
        ----------
        flowchart: seamm.Flowchart
            The non-graphical flowchart that contains this step.

        title: str
            The name displayed in the flowchart.
        namespace : str
            The namespace for the plug-ins of the subflowchart
        extension: None
            Not yet implemented
        logger : Logger = logger
            The logger to use and pass to parent classes

        Returns
        -------
        None
        """
        logger.debug(f"Creating Subflowchart {self}")
        self.subflowchart = seamm.Flowchart(
            parent=self, name="Subflowchart", namespace=namespace
        )  # yapf: disable

        super().__init__(
            flowchart=flowchart,
            title="Subflowchart",
            extension=extension,
            module=__name__,
            logger=logger,
        )  # yapf: disable

        self._file_handler = None

    @property
    def version(self):
        """The semantic version of this module."""
        return subflowchart_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return subflowchart_step.__git_revision__

    def analyze(self, indent="", **kwargs):
        """Do any analysis of the output from this step.

        Also print important results to the local step.out file using
        "printer".

        Parameters
        ----------
        indent: str
            An extra indentation for the output
        """
        # Get the first real node
        node = self.subflowchart.get_node("1").next()

        # Loop over the subnodes, asking them to do their analysis
        while node is not None:
            for value in node.description:
                printer.important(value)
                printer.important(" ")

            node.analyze()

            node = node.next()

    def create_parser(self):
        """Setup the command-line / config file parser"""
        parser_name = "subflowchart-step"
        parser = getParser()

        # Remember if the parser exists ... this type of step may have been
        # found before
        parser_exists = parser.exists(parser_name)

        # Create the standard options, e.g. log-level
        super().create_parser(name=parser_name)

        if not parser_exists:
            # Any options for subflowchart itself
            pass

        # Now need to walk through the steps in the subflowchart...
        self.subflowchart.reset_visited()
        node = self.subflowchart.get_node("1").next()
        while node is not None:
            node = node.create_parser()

        return self.next()

    def description_text(self, P=None):
        """Create the text description of what this step will do.
        The dictionary of control values is passed in as P so that
        the code can test values, etc.

        Parameters
        ----------
        P: dict
            An optional dictionary of the current values of the control
            parameters.
        Returns
        -------
        str
            A description of the current step.
        """
        # Make sure the subflowchart has the data from the parent flowchart
        self.subflowchart.root_directory = self.flowchart.root_directory
        self.subflowchart.executor = self.flowchart.executor
        self.subflowchart.in_jobserver = self.subflowchart.in_jobserver

        # Get the first real node
        node = self.subflowchart.get_node("1").next()

        text = self.header + "\n\n"
        while node is not None:
            node.all_options = self.all_options
            try:
                text += __(node.description_text(), indent=3 * " ").__str__()
            except Exception as e:
                print(f"Error describing subflowchart flowchart: {e} in {node}")
                logger.critical(
                    f"Error describing subflowchart flowchart: {e} in {node}"
                )
                raise
            except:  # noqa: E722
                print(
                    "Unexpected error describing subflowchart flowchart: "
                    f"{sys.exc_info()[0]} in {str(node)}."
                )
                logger.critical(
                    "Unexpected error describing subflowchart flowchart: "
                    f"{sys.exc_info()[0]} in {str(node)}."
                )
                raise
            text += "\n"
            node = node.next()

        return text

    def run(self):
        """Run a Subflowchart step.

        Parameters
        ----------
        None

        Returns
        -------
        seamm.Node
            The next node object in the flowchart.
        """
        next_node = super().run(printer)

        wd = Path(self.directory)

        # Find the handler for job.out and set the level up
        job_handler = None
        out_handler = None
        for handler in job.handlers:
            if (
                isinstance(handler, logging.FileHandler)
                and "job.out" in handler.baseFilename
            ):
                job_handler = handler
                job_level = job_handler.level
                job_handler.setLevel(printing.JOB)
            elif isinstance(handler, logging.StreamHandler):
                out_handler = handler
                out_level = out_handler.level
                out_handler.setLevel(printing.JOB)

        # Make sure the subflowchart has the data from the parent flowchart
        self.subflowchart.root_directory = self.flowchart.root_directory
        self.subflowchart.executor = self.flowchart.executor
        self.subflowchart.in_jobserver = self.subflowchart.in_jobserver

        # Get the first real node
        first_node = self.subflowchart.get_node("1").next()

        # Ensure the nodes have their options
        node = first_node
        while node is not None:
            node.all_options = self.all_options
            node = node.next()

        # Run the subflowchart
        # A handler for the file
        if self._file_handler is not None:
            self._file_handler.close()
            job.removeHandler(self._file_handler)
        path = wd / "Subflowchart.out"
        path.unlink(missing_ok=True)
        self._file_handler = logging.FileHandler(path)
        self._file_handler.setLevel(printing.NORMAL)
        formatter = logging.Formatter(fmt="{message:s}", style="{")
        self._file_handler.setFormatter(formatter)
        job.addHandler(self._file_handler)

        # Run through the steps in the loop body
        node = first_node
        try:
            while node is not None:
                try:
                    node = node.run()
                except DeprecationWarning as e:
                    printer.normal("\nDeprecation warning: " + str(e))
                    traceback.print_exc(file=sys.stderr)
                    traceback.print_exc(file=sys.stdout)
        except ContinueLoop:
            raise
        except BreakLoop:
            raise
        except SkipIteration:
            raise
        except Exception as e:
            printer.job(f"Caught exception in subflowchart: {str(e)}")
            with open(wd / "stderr.out", "a") as fd:
                traceback.print_exc(file=fd)
            raise
        finally:
            if job_handler is not None:
                job_handler.setLevel(job_level)
            if out_handler is not None:
                out_handler.setLevel(out_level)

            if job_handler is not None:
                job_handler.setLevel(printing.JOB)
            if out_handler is not None:
                out_handler.setLevel(printing.JOB)

            # Remove any redirection of printing.
            if self._file_handler is not None:
                self._file_handler.close()
                job.removeHandler(self._file_handler)
                self._file_handler = None
            if job_handler is not None:
                job_handler.setLevel(job_level)
            if out_handler is not None:
                out_handler.setLevel(out_level)

        # Add other citations here or in the appropriate place in the code.
        # Add the bibtex to data/references.bib, and add a self.reference.cite
        # similar to the above to actually add the citation to the references.

        return next_node

    def set_id(self, node_id):
        """Set the id for node to a given tuple"""
        self._id = node_id

        # Set the options in the subflowchart's nodes
        for node in self.subflowchart:
            node.all_options = self.all_options

        # and set our subnodes
        self.subflowchart.set_ids(self._id)

        return self.next()
