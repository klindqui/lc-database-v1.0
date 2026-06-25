- improve the failure message 
- create a wrapper script that will allow pipeline to run automatically
- ensure that google auth will not break again
- make sure the wrapper is run every 5 minutes or constantly or something
- finish documentation and add to github. make sure to include why the 3 files failed to upload. later there should be a feature where it will automatically put this note in the log and then when all logs are automatically uploaded into the github it will be included that way


The 3 failed files were:
- mems_2026_03_19.csv
- mems_2026_04_16.csv
- mems_2026_06_01.csv

Reason:
Each file contained only a header row and no measurement data, so the uploader correctly rejected them and moved them to runtime/failed.