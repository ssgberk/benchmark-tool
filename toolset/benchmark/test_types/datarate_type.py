from toolset.benchmark.test_types.framework_test_type import FrameworkTestType
from time import sleep


class DatarateTestType(FrameworkTestType):
    def __init__(self, config):
        kwargs = {
            'name': 'datarate'
        }
        FrameworkTestType.__init__(self, config, **kwargs)

    def get_script_name(self):
        return 'build.sh'

    def get_script_variables(self):
        return {
            'duration':
            self.config.duration,
            'number_of_files':
            self.config.number_of_files,
            'content_size':
            self.config.content_size,
            'min_runs':
            self.config.min_runs,
            'verbose_build':
            self.config.verbose_build,
        }
