from flask import Flask, request, jsonify
import os
from scripts.file_comparison import compare
from scripts.file_comparison import specific_compare
from scripts.utils import human_readable_size

app = Flask(__name__)

in_dir = "input_files"
out_dir = "results"
block_size = 2


@app.route("/calculate", methods=["GET"])
def calculate(input_file: str):
    input_directory = "input_files"
    print(f"perform_calculation called with input_file: {input_file}")
    if not os.path.exists(input_directory):
        return jsonify({"error": "Input directory does not exist"}), 400

    file_list = sorted(os.listdir(input_directory))
    if len(file_list) < 2:
        return jsonify({"error": "Not enough files for comparison"}), 400

    # Add your calculation logic here
    specific_compare(input_file,in_dir, out_dir, block_size)

    return jsonify({"message": "Calculation successful"}), 200


@app.route("/get-file-list", methods=["GET"])
def get_file_list():
    input_directory = "input_files"

    if not os.path.exists(input_directory):
        os.makedirs(input_directory)

    file_list = sorted(os.listdir(input_directory))
    if not file_list:
        return jsonify({"error": "Not enough files for comparison"}), 400

    file_objects = []
    for idx, file_name in enumerate(file_list):
        file_path = os.path.join(input_directory, file_name)
        file_extension = os.path.splitext(file_name)[1][1:].upper()
        file_size = os.path.getsize(file_path)
        file_size = human_readable_size(file_size)
        file_objects.append(
            {
                "id": idx + 1,
                "file_name": file_name,
                "file_extension": file_extension,
                "file_size": file_size,
            }
        )

    return jsonify(file_objects), 200


@app.route("/store-files", methods=["POST"])
def store_files():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if not file:
            return jsonify({"error": "No selected file"}), 400

        allowed_extensions = {"pdf", "txt", "docx", "odt"}
        input_directory = "input_files"
        results_directory = "results"  # Ensure results directory is absolute

        # Create directories if they do not exist
        if not os.path.exists(input_directory):
            os.makedirs(input_directory)

        if not os.path.exists(results_directory):
            os.makedirs(results_directory)

        file_extension = file.filename.rsplit(".", 1)[1].lower()
        if file_extension not in allowed_extensions:
            return jsonify({"error": "Unsupported file type"}), 400

        file_path = os.path.join(input_directory, file.filename)
        file.save(file_path)
        print(f"File saved to {file_path}")
        calculate_response = calculate(file_path)
        return jsonify({"message": f"File '{file.filename}' successfully stored ."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/delete-files", methods=["DELETE"])
def delete_files():
    data = request.get_json()
    if not data or "serial_numbers" not in data:
        return jsonify({"error": "No serial numbers provided"}), 400

    serial_numbers = data["serial_numbers"]
    if not isinstance(serial_numbers, list) or not all(
        isinstance(sn, int) for sn in serial_numbers
    ):
        return jsonify({"error": "Invalid serial numbers format"}), 400

    input_directory = "input_files"
    if not os.path.exists(input_directory):
        return jsonify({"error": "Input directory does not exist"}), 400

    file_list = sorted(os.listdir(input_directory))
    deleted_files_count = 0
    not_found_files_count = 0

    for serial_number in serial_numbers:
        # Adjust serial_number to be 1-based index
        adjusted_index = serial_number - 1
        if adjusted_index < 0 or adjusted_index >= len(file_list):
            not_found_files_count += 1
            continue

        file_name = file_list[adjusted_index]
        file_path = os.path.join(input_directory, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted_files_count += 1
        else:
            not_found_files_count += 1

    message_parts = []
    if deleted_files_count > 0:
        message_parts.append(
            f"{deleted_files_count} file{'s' if deleted_files_count != 1 else ''} successfully deleted"
        )
    if not_found_files_count > 0:
        message_parts.append(
            f"{not_found_files_count} file{'s' if not_found_files_count != 1 else ''} not found"
        )

    return jsonify({"message": ", ".join(message_parts)}), 200


if __name__ == "__main__":
    app.run(debug=True)
