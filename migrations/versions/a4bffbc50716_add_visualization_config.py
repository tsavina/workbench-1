"""add_visualization_config

Revision ID: a4bffbc50716
Revises: 8e7b97ccae4d
Create Date: 2021-04-07 16:04:41.533020

"""

"""
 OpenVINO DL Workbench
 Migration: Add visualization configuration

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
import json
from typing import List
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, Text, orm
from sqlalchemy.orm import relationship, backref

# revision identifiers, used by Alembic.
revision = 'a4bffbc50716'
down_revision = '8e7b97ccae4d'
branch_labels = None
depends_on = None

Base = declarative_base()

DEFAULT_VISUALIZATION_CONFIGURATION = json.dumps({
    'taskType': 'generic',
    'taskMethod': 'generic',
    'adapterConfiguration': {},
    'preprocessing': [
        {
            'type': 'auto_resize',
        },
    ],
    'postprocessing': [],
})


class _OMZTopologyModel(Base):
    __tablename__ = 'omz_topologies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    advanced_configuration = Column(Text, nullable=True)
    task_type = Column(
        postgresql.ENUM('classification', 'object_detection', 'instance_segmentation', 'semantic_segmentation',
                        'inpainting', 'style_transfer', 'super_resolution', 'face_recognition', 'landmark_detection',
                        'generic', 'custom',
                        name='taskenum'), nullable=False)
    topology_type = Column(
        postgresql.ENUM('classificator', 'generic', 'ssd', 'tiny_yolo_v2', 'yolo_v2', 'mask_rcnn', 'segmentation',
                        'inpainting', 'style_transfer', 'super_resolution', 'face_recognition', 'landmark_detection',
                        'custom',
                        name='taskmethodenum'), nullable=False)


class _TopologiesModel(Base):
    __tablename__ = 'topologies'

    id = Column(Integer, primary_key=True)
    downloaded_from = Column(Integer, ForeignKey('omz_topologies.id'), nullable=True)
    metadata_id = Column(Integer, ForeignKey('topologies_metadata.id'), nullable=False)
    source = Column(postgresql.ENUM('omz', 'original', 'ir',
                                    name='modelsourceenum'), nullable=True)
    downloaded_from_record = relationship('_OMZTopologyModel', foreign_keys=[downloaded_from], lazy='joined',
                                          backref=backref('downloaded_to', lazy='subquery', cascade='delete,all'))
    meta = relationship('_TopologiesMetaDataModel', lazy='joined')


class _TopologiesMetaDataModel(Base):
    __tablename__ = 'topologies_metadata'

    id = Column(Integer, primary_key=True, autoincrement=True)

    visualization_configuration = Column(Text, nullable=True)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('topologies_metadata', sa.Column('visualization_configuration', sa.Text(), nullable=True))
    # ### end Alembic commands ###

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    topologies: List[_TopologiesModel] = session.query(_TopologiesModel).all()

    for topology in topologies:
        if topology.source != 'omz':
            visualization_config = DEFAULT_VISUALIZATION_CONFIGURATION
        else:
            omz_model: _OMZTopologyModel = topology.downloaded_from_record
            visualization_config = json.dumps({
                'taskType': omz_model.task_type,
                'taskMethod': omz_model.topology_type,
                **json.loads(omz_model.advanced_configuration),
            })

        topology.meta.visualization_configuration = visualization_config
        session.add(topology.meta)

    session.flush()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('topologies_metadata', 'visualization_configuration')
    # ### end Alembic commands ###
