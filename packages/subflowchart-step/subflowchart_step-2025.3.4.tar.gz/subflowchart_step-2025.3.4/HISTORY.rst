=======
History
=======
2025.3.4: Handling breaks and continues of loops
    * Correctly pass loop exceptions, such as break and continue, that are raised in the
      flowchart up to any loop that the subflowchart is in.
    * Fixed issues with the redirection of printing if errors occur.
      
2024.11.18: Bugfix: Options not passed correctly to substeps
    * Fixed the options, which were not being correctly handled for steps in the
      subflowchart.
      
2024.11.5: Initial release
    * This is the initial release of the plug-in.

2024.10.26: Initial commit
    * Plug-in created using the SEAMM plug-in cookiecutter.
