from flask import Flask, render_template, request
import hashlib
import re
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, NumberRange
from werkzeug.datastructures import ImmutableMultiDict


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

class MyForm(FlaskForm):
    salt = StringField('Salt', validators=[DataRequired()])
    probability = FloatField('Probability', validators=[DataRequired(), NumberRange(min=0, max=1)])
    data = TextAreaField('Data', validators=[DataRequired()])
    retrieve_domain = BooleanField('Retrieve only the domain of the e-mail?', default=False)


@app.route('/', methods=['GET'])
def index():
    salt = request.args.get('salt', '')
    probability = float(request.args.get('probability', default=0.0))
    data = request.args.get('data', '')
    retrieve_domain = request.args.get('retrieve_domain', type=bool, default=False)
    formdata = ImmutableMultiDict([('salt', salt), ('probability', probability), ('data', data), ('retrieve_domain', retrieve_domain)])
    form = MyForm(formdata=formdata)
    table_data = [(email, branch_decision(email, salt, probability)) for email in split_multiline(data, retrieve_domain)] if data else []
    return render_template('combined.html', form=form, table_data=table_data)


# Client-provided function
def branch_decision(input_row: str, salt: str, probability: float):
    return (int(hashlib.md5((salt + input_row).encode("ascii")).hexdigest(), 16) / 2**128) < probability


# Function that splits the data content
def split_multiline(input_text, retrieve_domain=False):
    # Use regular expression to split the input using \n, \r\n, or \r as delimiters
    split_pattern = r'[\n\r\t\r\n]+'
    result = re.split(split_pattern, input_text)
    if retrieve_domain:
        result = [item.strip().split('@')[1] for item in result if '@' in item]
    else:
        result = [item.strip() for item in result]
    return result


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)