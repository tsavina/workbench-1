"""
 OpenVINO DL Workbench
 Class for create setup bundle job

 Copyright (c) 2020 Intel Corporation

 LEGAL NOTICE: Your use of this software and any required dependent software (the “Software Package”) is subject to
 the terms and conditions of the software license agreements for Software Package, which may also include
 notices, disclaimers, or license terms for third party or open source software
 included in or with the Software Package, and your use indicates your acceptance of all such terms.
 Please refer to the “third-party-programs.txt” or other similarly-named text file included with the Software Package
 for additional details.
 You may obtain a copy of the License at
      https://software.intel.com/content/dam/develop/external/us/en/documents/intel-openvino-license-agreements.pdf
"""
import os
import shutil
import tempfile
from contextlib import closing

from config.constants import ARTIFACTS_PATH
from wb.extensions_factories.database import get_db_session_for_celery
from wb.main.enumerates import JobTypesEnum, StatusEnum
from wb.main.jobs.interfaces.ijob import IJob
from wb.main.jobs.utils.database_functions import set_status_in_db
from wb.main.models import CreateSetupBundleJobModel, DownloadableArtifactsModel
from wb.main.scripts.job_scripts_generators.setup_script_generator import SetupScriptGenerator
from wb.main.utils.bundle_creator.setup_bundle_creator import SetupBundleCreator, SetupComponentsParams
from wb.main.utils.utils import get_size_of_files, find_by_ext


class CreateSetupBundleJob(IJob):
    job_type = JobTypesEnum.create_setup_bundle_type
    _job_model_class = CreateSetupBundleJobModel

    def __init__(self, job_id: int, **unused_kwargs):
        super().__init__(job_id=job_id)
        self._attach_default_db_and_socket_observers()
        with closing(get_db_session_for_celery()) as session:
            create_bundle_job_model: CreateSetupBundleJobModel = self.get_job_model(session)
            deployment_bundle_config = create_bundle_job_model.deployment_bundle_config
            self.deployment_bundle_id = deployment_bundle_config.deployment_bundle_id
            self.additional_components = [name for name, value in deployment_bundle_config.json().items() if value]
            self.targets = deployment_bundle_config.targets_to_json
            self.operating_system = deployment_bundle_config.operating_system
            self.include_model = deployment_bundle_config.include_model
            self.topology_name = create_bundle_job_model.project.topology.name if self.include_model else None
            self.topology_path = create_bundle_job_model.project.topology.path if self.include_model else None

    def run(self):
        self._job_state_subject.update_state(status=StatusEnum.running, log='Preparing setup bundle.')

        with tempfile.TemporaryDirectory('rw') as tmp_scripts_folder:
            setup_path = self.generate_script_from_template(tmp_scripts_folder, 'setup.sh')
            get_devices_path = self.generate_script_from_template(tmp_scripts_folder,
                                                                  'get_inference_engine_devices.sh')
            get_resources_path = self.generate_script_from_template(tmp_scripts_folder, 'get_system_resources.sh')
            has_internet_connection_path = self.generate_script_from_template(tmp_scripts_folder,
                                                                              'has_internet_connection.sh')
            topology_temporary_path = None

            if self.include_model:
                topology_temporary_path = os.path.join(tmp_scripts_folder, self.topology_name)
                os.makedirs(topology_temporary_path)
                xml_file = find_by_ext(self.topology_path, 'xml')
                tmp_xml_file = os.path.join(topology_temporary_path, f'{self.topology_name}.xml')
                shutil.copy(xml_file, tmp_xml_file)

                bin_file = find_by_ext(self.topology_path, 'bin')
                tmp_bin_file = os.path.join(topology_temporary_path, f'{self.topology_name}.bin')
                shutil.copy(bin_file, tmp_bin_file)

            setup_bundle_creator = SetupBundleCreator(
                log_callback=lambda message, progress:
                self._job_state_subject.update_state(log=message,
                                                     progress=progress)
            )
            setup_components = SetupComponentsParams(setup_path, get_devices_path,
                                                     get_resources_path,
                                                     has_internet_connection_path,
                                                     self.operating_system,
                                                     self.targets,
                                                     self.additional_components,
                                                     topology_temporary_path)
            setup_bundle_creator.create(components=setup_components,
                                        destination_bundle=os.path.join(ARTIFACTS_PATH, str(self.deployment_bundle_id)))
        self.on_success()

    @staticmethod
    def generate_script_from_template(result_scripts_path: str, script_name: str) -> str:
        result_script_path = os.path.join(result_scripts_path, script_name)
        job_script_generator = SetupScriptGenerator(script_name)
        job_script_generator.create(result_file_path=result_script_path)
        return result_script_path

    def on_success(self):
        with closing(get_db_session_for_celery()) as session:
            deployment_job = self.get_job_model(session)
            bundle = deployment_job.deployment_bundle_config.deployment_bundle
            bundle_path = DownloadableArtifactsModel.get_archive_path(bundle.id)
            bundle.path = bundle_path
            bundle.size = get_size_of_files(bundle_path)
            bundle.write_record(session)
            set_status_in_db(DownloadableArtifactsModel, bundle.id, StatusEnum.ready, session, force=True)
            self._job_state_subject.update_state(status=StatusEnum.ready,
                                                 log='Setup bundle created successfully.')
            self._job_state_subject.detach_all_observers()
