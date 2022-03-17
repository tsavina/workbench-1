"""Add reshape model pipeline

Revision ID: b6ba1e22cc13
Revises: af29f21e2ea5
Create Date: 2021-11-22 15:29:48.236433

"""

"""
 OpenVINO DL Workbench
 Migration: Add reshape model pipeline

 Copyright (c) 2021 Intel Corporation

 LEGAL NOTICE: Your use of this software and any required dependent software (the “Software Package”) is subject to
 the terms and conditions of the software license agreements for Software Package, which may also include
 notices, disclaimers, or license terms for third party or open source software
 included in or with the Software Package, and your use indicates your acceptance of all such terms.
 Please refer to the “third-party-programs.txt” or other similarly-named text file included with the Software Package
 for additional details.
 You may obtain a copy of the License at
      https://software.intel.com/content/dam/develop/external/us/en/documents/intel-openvino-license-agreements.pdf
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migrations.utils import SQLEnumMigrator

# revision identifiers, used by Alembic.
revision = 'b6ba1e22cc13'
down_revision = 'af29f21e2ea5'
branch_labels = None
depends_on = None

old_pipeline_types = (
    'local_accuracy',
    'remote_accuracy',
    'dev_cloud_accuracy',
    'remote_profiling',
    'local_profiling',
    'dev_cloud_profiling',
    'local_int8_calibration',
    'remote_int8_calibration',
    'dev_cloud_int8_calibration',
    'create_profiling_bundle',
    'download_log',
    'download_model',
    'deployment_manager',
    'export_project',
    'setup',
    'ping',
    'inference_test_image',
    'generate_dataset',
    'upload_dataset',
    'upload_model',
    'download_omz_model',
    'export_project_report',
    'export_inference_report',
    'local_winograd_tuning',
    'local_per_tensor_report',
    'remote_per_tensor_report',
    'local_predictions_relative_accuracy_report',
    'remote_predictions_relative_accuracy_report',
    'dev_cloud_predictions_relative_accuracy_report',
    'dev_cloud_per_tensor_report',
    'upload_tokenizer'
)

new_pipeline_types = (
    *old_pipeline_types,
    'reshape_model'
)

pipeline_type_enum_migrator = SQLEnumMigrator(
    table_column_pairs=(('pipelines', 'type'),),
    enum_name='pipelinetypeenum',
    from_types=old_pipeline_types,
    to_types=new_pipeline_types
)

old_pipeline_stages = (
    'accuracy',
    'preparing_setup_assets',
    'uploading_setup_assets',
    'configuring_environment',
    'collecting_available_devices',
    'collecting_system_information',
    'preparing_profiling_assets',
    'preparing_int8_calibration_assets',
    'preparing_accuracy_assets',
    'profiling',
    'getting_remote_job_result',
    'download_log',
    'int8_calibration',
    'remote_int8_calibration',
    'augment_dataset',
    'extract_dataset',
    'generate_dataset',
    'recognize_dataset',
    'validate_dataset',
    'wait_dataset_upload',
    'export_project_report',
    'export_inference_report',
    'wait_model_upload',
    'model_analyzer',
    'model_optimizer_scan',
    'convert_keras_model',
    'convert_model',
    'setup_environment',
    'download_omz_model',
    'convert_omz_model',
    'move_omz_model',
    'inference_test_image',
    'export_project',
    'winograd_tuning',
    'extract_text_dataset',
    'validate_text_dataset',
    'convert_dataset',
    'wait_tokenizer_upload',
    'validate_tokenizer',
)
new_pipeline_stages = (
    *old_pipeline_stages,
    'preparing_reshape_model_assets',
    'reshape_model'
)

pipeline_stage_enum_migrator = SQLEnumMigrator(
    table_column_pairs=(('job_execution_details', 'stage'),),
    enum_name='pipelinestageenum',
    from_types=old_pipeline_stages,
    to_types=new_pipeline_stages
)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reshape_model_jobs',
                    sa.Column('job_id', sa.Integer(), nullable=False),
                    sa.Column('model_id', sa.Integer(), nullable=False),
                    sa.Column('save_reshaped_model', sa.Boolean(), nullable=False, ),
                    sa.Column('shape_model_configuration_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['job_id'], ['jobs.job_id'], ),
                    sa.ForeignKeyConstraint(['model_id'], ['topologies.id'], ),
                    sa.ForeignKeyConstraint(['shape_model_configuration_id'], ['model_shape_configurations.id'], ),
                    sa.PrimaryKeyConstraint('job_id')
                    )
    op.create_table('create_reshape_model_scripts_jobs',
                    sa.Column('job_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['job_id'], ['jobs.job_id'], ),
                    sa.PrimaryKeyConstraint('job_id')
                    )
    op.alter_column('model_shape_configurations', 'status',
                    existing_type=postgresql.ENUM('queued', 'running', 'ready', 'error', 'cancelled', 'archived',
                                                  'warning', name='statusenum'),
                    nullable=True)
    op.create_table('analyze_model_input_shape_jobs',
                    sa.Column('job_id', sa.Integer(), nullable=False),
                    sa.Column('model_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['job_id'], ['jobs.job_id'], ),
                    sa.ForeignKeyConstraint(['model_id'], ['topologies.id'], ),
                    sa.PrimaryKeyConstraint('job_id')
                    )
    # ### end Alembic commands ###
    pipeline_stage_enum_migrator.upgrade()
    pipeline_type_enum_migrator.upgrade()


def downgrade():
    raise NotImplementedError(f'Downgrade function is not implemented for {revision} revision')
