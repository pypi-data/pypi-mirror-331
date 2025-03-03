import json
from .etl import ETLProcess

class RefreshETL(ETLProcess):

    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "manifest",
                    "descr": "the manifest list",
                    "iterable": True
                }
            ],
            "outputs": [
                {
                    "name": "idx_files",
                    "descr": "the extracted data GBD FILES organized by appnum"
                },
                {
                    "name": "extraction_dir",
                    "descr": "the extracted dir"
                },
                {
                    'name': 'flag',
                    'descr': 'flag for done'
                }
            ]
        }
    }

    def postprocess(self):
        self.flag = [1]
