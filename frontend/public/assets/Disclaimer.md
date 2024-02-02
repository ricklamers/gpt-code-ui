# Data analysis using Natural Language

This is a tool for generating executable code from natural language input. Among other applications, this can be used for rapid data analysis e.g., for creating simple statistics, plots, but also more advanced calculations such as regressions.

To do this, you can specify in natural language how you want to analyze the data. The underlying GPT API creates the corresponding code that is then executed. **You can either upload a CSV or XLSX file or connect a Data Treasury Item from UPTIMIZE Foundry using its RID or folder path.** Please note that you need to at least have read authorization for the use case in Foundry that contains the data to be analyzed. The tool cannot write data to Foundry and does not send or store any data beyond your interactive session.

**The tool is experimental and there is no guarantee that the analysis results are correct.** Be as precise as possible when entering the analysis request and specify which variables are to be analyzed and how. You can check the correctness of the analysis by examining the executed code.

For some ideas on what is possible with this tool, see the demo video that is available through the sidebar on the left or by clicking the button below.
