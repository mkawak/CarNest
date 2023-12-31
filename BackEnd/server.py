from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory
from bson.json_util import dumps
from bson.objectid import ObjectId
import subprocess


# Start Mongodb
subprocess.Popen(["/Users/majd/PycharmProjects/CarNest/BackEnd/start_mongodb.sh"])
# Flask app
app = Flask(__name__)
CORS(app)
# Configure the MongoDB settings
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
# Initialize PyMongo with the Flask app
mongo = PyMongo(app)
# Folder to store all pictures
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# Flask folder config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Allowed uploaded content types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# Allowed uploaded content sizes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size, e.g., 16MB


# Helper for allowed content
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Helper checks if user is admin
def is_user_admin(email):
    user = mongo.db.users.find_one({'email': email})
    if user:
        return user.get('is_admin', False)
    else:
        return False

@app.route('/')
def home():
    return render_template('welcome_page.html')

@app.route('/sign-in')
def sign_in():
    return render_template('sign_in.html')

@app.route('/sign-up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/user-view')
def user_view():
    return render_template('user_view.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

# Route to signup
@app.route('/signup', methods=['POST'])
def signup():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    # Check if name, age, email and password are provided
    required_fields = ['name', 'age', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Name, Age, Email, and Password required'}), 400

    # Validate the age
    try:
        age = int(data['age'])
        if age < 18:
            return jsonify({'error': 'Age must be 18 or older'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid age, must be a number'}), 400

    # Validate user already exits
    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'error': 'User already exists'}), 409

    # Hashing password
    hashed_password = generate_password_hash(data['password'])
    # Insert in db
    mongo.db.users.insert_one({
        'name': data['name'],
        'age': data['age'],
        'email': data['email'],
        'password': hashed_password,
        'is_admin': False
    })
    return jsonify({'message': 'User created successfully'}), 201


# Route to signin
@app.route('/signin', methods=['POST'])
def signin():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400

    user = mongo.db.users.find_one({'email': data['email']})
    if user and check_password_hash(user['password'], data['password']):
        user_role = 'admin' if user.get('is_admin', False) else 'user'
        user_name = user.get('name', '')  # default to an empty string if name is not found
        return jsonify({'message': 'Logged in successfully', 'role': user_role, 'name': user_name}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


# Route to add listing
@app.route('/add_listing', methods=['POST'])
def add_listing():
    # Check for file part in the request
    files = request.files.getlist('pictures')

    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'No selected file'}), 400

    filenames = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            filenames.append(filename)
        else:
            return jsonify({'error': 'Invalid file type or no file uploaded'}), 400

    # Handle other form data
    user_email = request.form.get('email')
    make = request.form.get('make')
    model = request.form.get('model')
    year = request.form.get('year')
    millage = request.form.get('millage')
    price = request.form.get('price')
    address = request.form.get('address')

    user = mongo.db.users.find_one({'email': user_email})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    new_listing = {
        'make': make,
        'model': model,
        'year': year,
        'price': price,
        'millage': millage,
        'address': address,
        'views': [],
        'view_count': 0,
        'pictures': filenames
    }

    # Check user role and add to the appropriate collection
    if user.get('is_admin', False):
        mongo.db.listings.insert_one(new_listing)
        return jsonify({'message': 'Listing added successfully'}), 201
    else:
        mongo.db.pending_listings.insert_one(new_listing)
        return jsonify({'message': 'Listing submitted for approval'}), 201


# Route to pictures
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Route to get listings
@app.route('/get_listings', methods=['GET'])
def get_listings():
    listings = list(mongo.db.listings.find())
    return dumps(listings), 200


# Route for pending
@app.route('/get_pending_listings', methods=['GET'])
def get_pending_listings():
    user_email = request.args.get('email')

    user = mongo.db.users.find_one({'email': user_email})
    if not user or not user.get('is_admin', False):
        return jsonify({'error': 'Unauthorized access'}), 401

    pending_listings = list(mongo.db.pending_listings.find())
    return dumps(pending_listings), 200


# Route for permanently deleting a listing "admins only"
@app.route('/delete_listing/<listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    user_email = request.args.get('email')

    if not is_user_admin(user_email):
        return jsonify({'error': 'Unauthorized access'}), 401

    # Find the listing to get the picture filenames
    listing = mongo.db.listings.find_one({'_id': ObjectId(listing_id)})
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404

    # Delete pictures associated with the listing
    for picture in listing.get('pictures', []):
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture)
        if os.path.exists(picture_path):
            os.remove(picture_path)

    # Delete the listing from the database
    result = mongo.db.listings.delete_one({'_id': ObjectId(listing_id)})
    if result.deleted_count:
        return jsonify({'message': 'Listing and associated pictures deleted successfully'}), 200
    else:
        return jsonify({'error': 'Error deleting listing'}), 500


# Route for admin to approve a listing
@app.route('/approve_listing/<listing_id>', methods=['POST'])
def approve_listing(listing_id):
    user_email = request.json.get('email')
    if not is_user_admin(user_email):
        return jsonify({'error': 'Unauthorized access'}), 401

    listing = mongo.db.pending_listings.find_one_and_delete({'_id': ObjectId(listing_id)})
    if listing:
        listing['status'] = 'approved'
        mongo.db.listings.insert_one(listing)
        return jsonify({'message': 'Listing approved'}), 200
    else:
        return jsonify({'error': 'Listing not found'}), 404


# Route for admin to deny a listing
@app.route('/deny_listing/<listing_id>', methods=['POST'])
def deny_listing(listing_id):
    user_email = request.json.get('email')
    if not is_user_admin(user_email):
        return jsonify({'error': 'Unauthorized access'}), 401

    # Find the listing to get the picture filenames
    listing = mongo.db.pending_listings.find_one({'_id': ObjectId(listing_id)})
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404

    # Delete pictures associated with the listing
    for picture in listing.get('pictures', []):
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture)
        if os.path.exists(picture_path):
            os.remove(picture_path)

    # Delete the listing from the database
    result = mongo.db.pending_listings.delete_one({'_id': ObjectId(listing_id)})
    if result.deleted_count:
        return jsonify({'message': 'Listing denied and associated pictures deleted successfully'}), 200
    else:
        return jsonify({'error': 'Error denying listing'}), 500


# Increase views count
@app.route('/view_listing/<listing_id>', methods=['POST'])
def view_listing(listing_id):
    user_email = request.json.get('email')

    # Check if user is an admin
    if is_user_admin(user_email):
        return jsonify({'message': 'Admin view, not counted'}), 200

    listing = mongo.db.listings.find_one({'_id': ObjectId(listing_id)})
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404

    # Check if the user has already viewed the listing
    if user_email not in listing.get('views', []):
        # Add user's email to the views list and increment the view count
        mongo.db.listings.update_one(
            {'_id': ObjectId(listing_id)},
            {'$addToSet': {'views': user_email}, '$inc': {'views_count': 1}}
        )
        return jsonify({'message': 'View added to listing'}), 200
    else:
        return jsonify({'message': 'User has already viewed this listing'}), 200


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
