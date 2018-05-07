#################################################
# Dependencies
#################################################
import numpy as np
from flask import Flask, render_template, jsonify, redirect
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, scoped_session, Query
from sqlalchemy import create_engine, func, inspect, Column, Integer, String
import os

#################################################
# Engine Setup
#################################################
engine = create_engine('sqlite:///DataSets/belly_button_biodiversity.sqlite', convert_unicode=True, echo=False)
Base = declarative_base()
Base.metadata.reflect(engine)

#################################################
# Database Setup
#################################################
class Metadata(Base):
    __table__ = Base.metadata.tables['samples_metadata']

class Samples(Base):
    __table__ = Base.metadata.tables['samples']

class Otu(Base):
    __table__ = Base.metadata.tables['otu']

#################################################
# Session Setup
#################################################
session = scoped_session(sessionmaker(bind=engine))

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Full dashboard
@app.route('/')
def index():
    """Return Homepage."""
    return render_template('index.html')

#sample names
@app.route('/names')
def names():
    mapper = inspect(Samples)
    nameList = []
    for row in mapper.columns:
        nameList.append(row.name)
    del nameList[0]
    return jsonify(nameList)

#OTU descriptions
@app.route('/otu')
def otu():
    results = session.query(Otu.lowest_taxonomic_unit_found).all()
    descriptions = list(np.ravel(results))
    return jsonify(descriptions)

#MetaData
@app.route('/metadata/<sample>')
def metadata(sample):
    sampleId = sample.split('_')
    results = session.query(Metadata).\
        filter(Metadata.SAMPLEID == sampleId[1]).first()
    filteredResults = {
        'AGE': results.AGE,
        'BBTYPE': results.BBTYPE,
        'ETHNICITY': results.ETHNICITY,
        'GENDER': results.GENDER,
        'LOCATION': results.LOCATION,
        'SAMPLEID': results.SAMPLEID
        }
    return jsonify(filteredResults)

# Weekly Washing Frequency as a number
@app.route('/wfreq/<sample>')
def washingFrequency(sample):
    sampleId = sample.split('_')
    results = session.query(Metadata).\
        filter(Metadata.SAMPLEID == sampleId[1]).first()
    wfeq = results.WFREQ
    return jsonify(wfeq)

@app.route('/samples/<sample>')
def samples(sample):
    sel = [
            Samples.otu_id,
            getattr(Samples, sample),
            Otu.lowest_taxonomic_unit_found
          ]
    results = session.query(*sel).\
        join(Otu, Samples.otu_id==Otu.otu_id).\
        order_by(getattr(Samples, sample).desc()).all()
    ids = []
    values = []
    descriptions = []
    i=0
    while i<len(results):
        ids.append(results[i][0])
        values.append(results[i][1])
        descriptions.append(results[i][2])
        i += 1
    sampleDetails = {
        'id': sample,
        'otu_ids': ids,
        'sample_values': values,
        'descriptions': descriptions
    }
    return jsonify(sampleDetails)

if __name__ == '__main__':
    app.run(debug=True)
