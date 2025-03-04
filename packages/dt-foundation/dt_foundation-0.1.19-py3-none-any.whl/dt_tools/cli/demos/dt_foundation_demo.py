"""
This module will execute the dt_misc package demonstrations, which include:

- Logging demo
- OS demo
- Project helper demo
- Helper demo

To Run:
    ``poetry run python -m dt_tools.cli.demos.dt_misc_demo``

"""
from loguru import logger as LOGGER

import dt_tools.cli.demos.dt_misc_helper_demo as misc_helper_demo
import dt_tools.cli.demos.dt_logging_demo as logging_demo
import dt_tools.cli.demos.dt_os_demo as os_helper_demo
import dt_tools.cli.demos.dt_project_helper_demo as project_helper_demo
import dt_tools.cli.demos.dt_sysinfo_demo as sysinfo_demo
import dt_tools.logger.logging_helper as lh
from dt_tools.os.os_helper import OSHelper
from dt_tools.os.project_helper import ProjectHelper

def demo():
    OSHelper.enable_ctrl_c_handler()
    DEMOS = {
        "Logging demo": logging_demo,
        "OS demo": os_helper_demo,
        "System Info": sysinfo_demo,
        "Misc Helper demo": misc_helper_demo,
        "Project Helper demo": project_helper_demo,
    }
    l_handle = lh.configure_logger(log_level="INFO", brightness=False)
    LOGGER.info('='*80)
    version = f'v{ProjectHelper.determine_version("dt-foundation")}'
    LOGGER.info(f'dt_misc_demo {version}', 80)
    LOGGER.info('='*80)
    LOGGER.info('')
    for name, demo_module in DEMOS.items():
        if input(f'Run {name} (y/n)? ').lower() == 'y':
            if demo_module == logging_demo:
                # Logging demo sets up and removes it's own loggers 
                LOGGER.remove(l_handle)
            demo_module.demo()  
            if demo_module == logging_demo:
                l_handle = lh.configure_logger(log_level="INFO", brightness=False)
            LOGGER.info('') 
                                                      
    LOGGER.success("That's all folks!!")

if __name__ == '__main__':
    demo()