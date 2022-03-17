"""
 OpenVINO DL Workbench
 Class for cli output of calibration tool

 Copyright (c) 2018 Intel Corporation

 LEGAL NOTICE: Your use of this software and any required dependent software (the “Software Package”) is subject to
 the terms and conditions of the software license agreements for Software Package, which may also include
 notices, disclaimers, or license terms for third party or open source software
 included in or with the Software Package, and your use indicates your acceptance of all such terms.
 Please refer to the “third-party-programs.txt” or other similarly-named text file included with the Software Package
 for additional details.
 You may obtain a copy of the License at
      https://software.intel.com/content/dam/develop/external/us/en/documents/intel-openvino-license-agreements.pdf
"""

from wb.main.enumerates import StatusEnum
from wb.main.jobs.models.model_optimizer_scan_job_state import ModelOptimizerScanJobStateSubject
from wb.main.jobs.tools_runner.console_output_parser import ConsoleToolOutputParser, skip_empty_line_decorator


class ModelOptimizerScanParser(ConsoleToolOutputParser):
    _job_state_subject: ModelOptimizerScanJobStateSubject

    def __init__(self, job_state_subject: ModelOptimizerScanJobStateSubject):
        super().__init__(job_state_subject=job_state_subject)
        self.counter = 0

    @skip_empty_line_decorator
    def parse(self, string: str):
        speed = 0.75
        percent = min(speed * self.counter, 99)
        self.counter += 1
        self._job_state_subject.update_state(progress=percent, status=StatusEnum.running)
