#!flask/bin/python
## importing all required modules
from flask import Flask, jsonify, request
import pandas as pd
from sklearn import linear_model
import numpy as np
from itertools import combinations
import dateutil, urllib
from sklearn import linear_model
from sklearn.metrics import r2_score
import dateutil, sqlalchemy, dateutil
from sklearn import feature_selection as fs
import pandas.io.sql as psql
from sklearn.cross_validation import train_test_split
from sklearn.feature_selection import SelectKBest

## initialize the flask app
app = Flask(__name__)
app.secret_key = "/\xfa-\x84\xfeW\xc3\xda\x11%/\x0c\xa0\xbaY\xa3\x89\x93$\xf5\x92\x9eW}"

def equationsLR(ScenarioSetId, numEqn, allmonth, maxvars):
    """Function to take the csv file, return the set of equations
        filename = csv input file
        numEqn = number of equations to be returned back
    """
    connection_string = "DRIVER={SQL Server};SERVER=primeonedev.cloudapp.net;UID=sa;PWD=Rt%^DCime17;DATABASE=Primeone;"
    connection_string = urllib.quote_plus(connection_string) 
    connection_string = "mssql+pyodbc:///?odbc_connect=%s" % connection_string
    engine = sqlalchemy.create_engine(connection_string)
    connection = engine.connect()
    meta = sqlalchemy.MetaData(bind=engine, reflect=True)

    if int(allmonth)==1:
        sql = "SELECT [CURVE_ID],[CURVE_NM],[IDX_NM],[GRID_MTH_DT],[INPUT_PR_AMT],[PNL],[ScenarioSetId]FROM [PrimeOne].[dbo].[VW_MLScenarioSetProdCurveDetail]   where ScenarioSetId = %d" % (int(ScenarioSetId))
    elif int(allmonth) == 0:
        sql = "SELECT [CURVE_ID],[CURVE_NM],[IDX_NM],[GRID_MTH_DT],[INPUT_PR_AMT],[PNL],[ScenarioSetId]FROM [PrimeOne].[dbo].[VW_MLFrontMonthScenarioSetProdCurveDetail]   where ScenarioSetId = %d" % (int(ScenarioSetId))
    df = psql.read_sql(sql, connection)
    df['grid_col'] = df.apply (lambda row: row['IDX_NM'] + ' ' + str(dateutil.parser.parse(row['GRID_MTH_DT']).strftime('%Y_%d')),axis=1)
    eods = list(df['CURVE_NM'].unique())

    i=0
    for eod in eods:
        temp = df[df['CURVE_NM'] == eod]
        columns = list(temp['grid_col'])
        new_columns = []
        for col in columns:
            new_columns.append(col.replace(' ', '_').replace('.',''))
        new_columns += ['PNL']
        INPUT_PR_AMT = list(temp['INPUT_PR_AMT'])
        PNL = list(temp['PNL'].unique())

        if i == 0:
            new_df = pd.DataFrame(columns = new_columns)
        values = INPUT_PR_AMT + PNL
        value_dict = {}
        for new_col in new_columns:
            ix = new_columns.index(new_col)
            value_dict[new_col] = values[i]
        new_df.loc[i] = values
        i+=1

    equations = {}
    num_features = len(new_df.columns)
    columns1 = new_df.columns
    
    y = new_df.pop('PNL')
    pnl_values = list(y)
    all_positive = all(i >= 0.0 for i in pnl_values)
    all_negative = all(i < 0.0 for i in pnl_values)

    for i in range(1, num_features):
        b = fs.SelectKBest(fs.f_regression, k=i)
        X = b.fit_transform(new_df, y)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
        regr = linear_model.Lasso(fit_intercept = True)
        regr.fit(X_train, y_train)
        
        index_taken = list(b.get_support())
        variables_taken = []
        for j in range(len(index_taken)):
            if index_taken[j] == True:
                variables_taken.append(columns1[j])
        if len(variables_taken)>int(maxvars):
            continue
        y_pred = regr.predict(X_test)
        r2_value = r2_score(y_test, y_pred)

        coef = list(regr.coef_)
        
        eqn = ''
        for el in coef:
            ix = coef.index(el)
            if el>=0.0:
                eqn =  eqn + ' + ' + str(abs(int(el))) +'*' + variables_taken[ix]
            else:
                eqn =  eqn + ' - ' + str(abs(int(el))) +'*' + variables_taken[ix]

        eqn = eqn.strip()[1:].strip()
        if regr.intercept_>=0.0:
            eqn = eqn + ' + ' + str(abs(int(regr.intercept_)))
        else:
            eqn = eqn + ' - ' + str(abs(int(regr.intercept_)))
        equations['eqn_'+str(i)] = {'equation':eqn, 'r2_score':r2_value}

    count = 0
    equations_sorted = sorted(equations.items(),key=lambda x: x[1]['r2_score'],reverse=True)
    new_equations = {}
    for eqn_new in equations_sorted:
        new_equations[eqn_new[0]] = eqn_new[1]
        count+=1
        if count>int(numEqn):
            break
    return new_equations

@app.route('/getEquations', methods=['GET'])
def getEquations():
    """ GET view to request the equations
    sample request = http://127.0.0.1:5000/getEquations?ScenarioSetId=7&numEqn=10&allmonth=1&maxvars=5
    """
    ScenarioSetId  = request.args.get('ScenarioSetId')
    numEqn = request.args.get('numEqn')
    allmonth = request.args.get('allmonth')
    maxvars = request.args.get('maxvars')

    eqns = equationsLR(ScenarioSetId , numEqn, allmonth, maxvars)
    
    return jsonify({'eqns': eqns})

if __name__ == '__main__':
    ## debug = True. Show errors
    app.run(debug=True)
