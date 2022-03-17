"""Remote per-tensor accuracy report

Revision ID: 53adb93fb869
Revises: 7f9788668528
Create Date: 2021-10-20 18:18:39.480957

"""

"""
 OpenVINO DL Workbench
 Migration: Remote per-tensor accuracy report

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


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from migrations.utils import SQLEnumMigrator

revision = '53adb93fb869'
down_revision = '7f9788668528'
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
    'per_tensor_report',
    'predictions_relative_accuracy_report',
)

temp_pipeline_types = tuple((*old_pipeline_types, 'local_per_tensor_report', 'remote_per_tensor_report'))

tmp_pipeline_type_enum_migrator = SQLEnumMigrator(
    table_column_pairs=(('pipelines', 'type'),),
    enum_name='pipelinetypeenum',
    from_types=old_pipeline_types,
    to_types=temp_pipeline_types
)

new_pipeline_types = list(set(temp_pipeline_types) - {'per_tensor_report'})

pipeline_type_enum_migrator = SQLEnumMigrator(
    table_column_pairs=(('pipelines', 'type'),),
    enum_name='pipelinetypeenum',
    from_types=temp_pipeline_types,
    to_types=tuple(new_pipeline_types)
)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('create_per_tensor_scripts_jobs',
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.job_id'], ),
        sa.PrimaryKeyConstraint('job_id')
    )
    op.create_table('create_per_tensor_bundle_jobs',
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('bundle_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['bundle_id'], ['downloadable_artifacts.id'], ),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.job_id'], ),
        sa.PrimaryKeyConstraint('job_id')
    )
    # ### end Alembic commands ###

    tmp_pipeline_type_enum_migrator.upgrade()
    op.execute("UPDATE pipelines SET type='local_per_tensor_report' WHERE type='per_tensor_report'")
    pipeline_type_enum_migrator.upgrade()


def downgrade():
    raise NotImplementedError(f'Downgrade is not implemented for the {revision} migration')
