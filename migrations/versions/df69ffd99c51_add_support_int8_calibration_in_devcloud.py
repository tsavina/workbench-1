"""Add support Int8 Calibration in DevCloud

Revision ID: df69ffd99c51
Revises: ec2e224f49f0
Create Date: 2020-09-15 09:57:21.084519

"""

"""
 OpenVINO DL Workbench
 Migration: Add support Int8 Calibration in DevCloud

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
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm, Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# revision identifiers, used by Alembic.
revision = 'df69ffd99c51'
down_revision = 'ec2e224f49f0'
branch_labels = None
depends_on = None

old_pipelinetypeenum = (
'accuracy', 'remote_profiling', 'local_profiling', 'dev_cloud_profiling', 'local_int8_calibration',
'remote_int8_calibration', 'create_profiling_bundle', 'create_int8_calibration_bundle', 'download_log',
'download_model', 'deployment_manager', 'setup', 'ping')

new_pipelinetypeenum = (
'accuracy', 'remote_profiling', 'local_profiling', 'dev_cloud_profiling', 'local_int8_calibration',
'remote_int8_calibration', 'create_profiling_bundle', 'download_log', 'download_model', 'deployment_manager', 'setup',
'ping', 'dev_cloud_int8_calibration')

old_pipelinetypeenum_type = sa.Enum(*old_pipelinetypeenum, name='pipelinetypeenum')
new_pipelinetypeenum_type = sa.Enum(*new_pipelinetypeenum, name='pipelinetypeenum')
tmp_pipelinetypeenum_type = sa.Enum(*new_pipelinetypeenum, name='tmp_pipelinetypeenum')


class ParseDevCloudResultJobModel(Base):
    __tablename__ = 'parse_dev_cloud_profiling_result_jobs'
    job_id = Column(Integer, primary_key=True)
    profiling_result_artifact_id = Column(Integer, nullable=False)


class PipelineModel(Base):
    __tablename__ = 'pipelines'
    id = Column(Integer, primary_key=True)
    type = Column(new_pipelinetypeenum_type, nullable=False)


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # ### command auto generated by Alembic - please adjust! ###
    parse_dev_cloud_jobs_table = op.create_table('parse_dev_cloud_result_jobs',
                                                 sa.Column('job_id', sa.Integer(), nullable=False),
                                                 sa.Column('result_artifact_id', sa.Integer(), nullable=False),
                                                 sa.ForeignKeyConstraint(['job_id'], ['jobs.job_id']),
                                                 sa.ForeignKeyConstraint(['result_artifact_id'],
                                                                         ['downloadable_artifacts.id'], ),
                                                 sa.PrimaryKeyConstraint('job_id')
                                                 )

    # ### data migration from parse_dev_cloud_profiling_result_jobs to parse_dev_cloud_result_jobs ###
    parse_dev_cloud_profiling_result_jobs = session.query(ParseDevCloudResultJobModel).all()
    parse_dev_cloud_jobs = []
    for parse_dev_cloud_profiling_result_job in parse_dev_cloud_profiling_result_jobs:
        parse_dev_cloud_jobs.append({
            'job_id': parse_dev_cloud_profiling_result_job.job_id,
            'result_artifact_id': parse_dev_cloud_profiling_result_job.profiling_result_artifact_id,
        })

    op.bulk_insert(parse_dev_cloud_jobs_table, parse_dev_cloud_jobs)

    # ### rename trigger_dev_cloud_profiling_jobs to trigger_dev_cloud_jobs ###
    op.rename_table('trigger_dev_cloud_profiling_jobs', 'trigger_dev_cloud_jobs')

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('parse_dev_cloud_int8_calibration_result_jobs',
                    sa.Column('job_id', sa.Integer(), nullable=False),
                    sa.Column('int8_model_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['int8_model_id'], ['topologies.id'], ),
                    sa.ForeignKeyConstraint(['job_id'], ['parse_dev_cloud_result_jobs.job_id'], ),
                    sa.PrimaryKeyConstraint('job_id', 'int8_model_id')
                    )

    op.drop_constraint('parse_dev_cloud_profiling_result_jobs_job_id_fkey',
                       'parse_dev_cloud_profiling_result_jobs',
                       type_='foreignkey')
    op.drop_constraint('parse_dev_cloud_profiling_res_profiling_result_artifact_id_fkey',
                       'parse_dev_cloud_profiling_result_jobs', type_='foreignkey')
    op.create_foreign_key(None, 'parse_dev_cloud_profiling_result_jobs', 'parse_dev_cloud_result_jobs', ['job_id'],
                          ['job_id'])
    op.drop_column('parse_dev_cloud_profiling_result_jobs', 'profiling_result_artifact_id')
    # ### end Alembic commands ###

    # Update PipelineTypeEnum enum
    # Create a temporary "tmp_pipelinetypeenum" type, convert and drop the "old" type
    tmp_pipelinetypeenum_type.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE pipelines ALTER COLUMN type TYPE tmp_pipelinetypeenum'
               ' USING type::text::tmp_pipelinetypeenum')
    old_pipelinetypeenum_type.drop(op.get_bind(), checkfirst=False)
    # Create and convert to the "new" type type
    new_pipelinetypeenum_type.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE pipelines ALTER COLUMN type TYPE pipelinetypeenum'
               ' USING type::text::pipelinetypeenum')
    tmp_pipelinetypeenum_type.drop(op.get_bind(), checkfirst=False)


class ParseDevCloudResultJobModelDowngrade(Base):
    __tablename__ = 'parse_dev_cloud_result_jobs'
    job_id = Column(Integer, primary_key=True)
    result_artifact_id = Column(Integer, nullable=False)


def downgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # ### rename trigger_dev_cloud_profiling_jobs to trigger_dev_cloud_profiling_jobs ###
    op.rename_table('trigger_dev_cloud_jobs', 'trigger_dev_cloud_profiling_jobs')

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('parse_dev_cloud_profiling_result_jobs',
                  sa.Column('profiling_result_artifact_id', sa.INTEGER(), autoincrement=False))

    # ### data migration from parse_dev_cloud_profiling_result_jobs to parse_dev_cloud_result_jobs ###
    parse_dev_cloud_jobs = session.query(ParseDevCloudResultJobModelDowngrade).all()
    for parse_dev_cloud_job in parse_dev_cloud_jobs:
        parse_dev_cloud_profiling_result_job = (
            session.query(ParseDevCloudResultJobModel).get(parse_dev_cloud_job.job_id)
        )
        if not parse_dev_cloud_profiling_result_job:
            continue
        parse_dev_cloud_profiling_result_job.profiling_result_artifact_id = parse_dev_cloud_job.result_artifact_id

    op.drop_constraint('parse_dev_cloud_profiling_result_jobs_job_id_fkey',
                       'parse_dev_cloud_profiling_result_jobs',
                       type_='foreignkey')

    op.create_foreign_key('parse_dev_cloud_profiling_res_profiling_result_artifact_id_fkey',
                          'parse_dev_cloud_profiling_result_jobs', 'artifacts', ['profiling_result_artifact_id'],
                          ['id'])
    op.create_foreign_key('parse_dev_cloud_profiling_result_jobs_job_id_fkey', 'parse_dev_cloud_profiling_result_jobs',
                          'jobs', ['job_id'], ['job_id'])

    op.drop_table('parse_dev_cloud_int8_calibration_result_jobs')
    op.drop_table('parse_dev_cloud_result_jobs')
    # ### end Alembic commands ###

    # Temporary enum is old enum
    tmp_pipelinetypeenum_type = sa.Enum(*old_pipelinetypeenum, name='tmp_pipelinetypeenum')

    # Update PipelineTypeEnum enum
    # Create a temporary "tmp_pipelinetypeenum" type, convert and drop the "new" type
    tmp_pipelinetypeenum_type.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE pipelines ALTER COLUMN type TYPE tmp_pipelinetypeenum'
               ' USING type::text::tmp_pipelinetypeenum')
    new_pipelinetypeenum_type.drop(op.get_bind(), checkfirst=False)
    # Create and convert to the "new" type type
    old_pipelinetypeenum_type.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE pipelines ALTER COLUMN type TYPE pipelinetypeenum'
               ' USING type::text::pipelinetypeenum')
    tmp_pipelinetypeenum_type.drop(op.get_bind(), checkfirst=False)
