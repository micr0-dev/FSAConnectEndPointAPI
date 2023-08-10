from io import BytesIO
from re import search
from requests import Session
from bs4 import BeautifulSoup as bs
from string import digits
import matplotlib.pyplot as plt


def pullGrades(username: str, password: str) -> dict:
    """
    Pull the grades for the given username and password.

    :param username: username of user to pull from
    :param password: password of user to pull from
    :return: dictionary of grades where the key is string course and the value is float grade
    """

    # print("logging in..")
    with Session() as s:
        site = s.get("https://fultonscienceacademy.radixlms.com/login/")
        bs_content = bs(site.content, "html.parser")
        token = bs_content.find("input", {"name": "logintoken"})["value"]
        login_data = {
            "username": username,
            "password": password,
            "logintoken": token,
            "anchor": "",
        }
        s.post("https://fultonscienceacademy.radixlms.com/login/index.php", login_data)
        grade_page = s.get(
            "https://fultonscienceacademy.radixlms.com/grade/report/overview/"
        )
        grade_content = bs(grade_page.content, "html.parser")
        grades = grade_content.find_all("tr", id=lambda x: x and x.startswith("grade-"))

    # print("grabbing grades")

    gradesDict = {}

    for i in grades:
        if search("%", i.text.strip()):
            text = i.text.strip()

            in1 = text.rfind("(") + 1
            in2 = text.rfind(")") - 3

            if text[text.rfind("(") + 1 : text.rfind(")") - 3].isnumeric() or search(
                ".", text[text.rfind("(") + 1 : text.rfind(")") - 3]
            ):
                substring = text[in1:in2]

                gradesDict[
                    text.translate({ord(k): None for k in digits})
                    .replace("(", "")
                    .replace(".", "")
                    .replace("%", "")
                    .replace(")", "")
                    .replace("  ", "")
                ] = float(substring)
    return gradesDict


def barGraph(data: dict):
    """
    Creates a bar graph for the given data.

    :param data: dictionary of grades where the key is a string course, and the value is a float grade
    :return: binary image object of the bar graph
    """

    courses = list(data.keys())
    values = list(data.values())
    fig = plt.figure(figsize=(16, 5))

    # creating the bar plot
    plt.bar(courses, values, color="seagreen", width=0.4)

    # adding the rounded values at the top of the bars
    for i, value in enumerate(values):
        plt.text(
            i,
            value / 2,
            round(value),
            ha="center",
            color="white",
            fontsize=24,
            weight="bold",
        )

    plt.xlabel("Courses")
    plt.ylabel("Grade")
    plt.title("Your Grades")

    # Convert plot to binary image object
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return buf


def pullAssignments(username, password) -> dict:
    with Session() as s:
        site = s.get("https://fultonscienceacademy.radixlms.com/login/")
        bs_content = bs(site.content, "html.parser")
        token = bs_content.find("input", {"name": "logintoken"})["value"]
        login_data = {
            "username": username,
            "password": password,
            "logintoken": token,
            "anchor": "",
        }
        s.post("https://fultonscienceacademy.radixlms.com/login/index.php", login_data)
        assignment_page = s.get(
            "https://fultonscienceacademy.radixlms.com/blocks/radix_dashboard/upcomingassignments.php"
        )
        assignment_content = bs(assignment_page.content, "html.parser")
        table = assignment_content.find("tbody")
        table_rows = table.find_all("tr")
        data = {}
        for tr in table_rows:
            td = tr.find_all("td")
            data[td[1].text] = td[0].text.strip()

        # matplotlib table code
        fig, ax = plt.subplots(figsize=(16, 5))
        ax.axis("tight")
        ax.axis("off")

        the_table = ax.table(
            cellText=list(data.items()),
            colLabels=["Assignment", "Due Date"],
            loc="center",
            cellLoc="center",
            colWidths=[0.9, 0.4],
        )
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(16)
        the_table.scale(1, 1.8)
        # bold colLabels
        for (row, col), cell in the_table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight="bold")

        plt.savefig("table.png", bbox_inches="tight")
        plt.close()


from flask import Flask, jsonify, send_file

app = Flask(__name__)


@app.route("/grades/<username>/<password>", methods=["GET"])
def get_grades(username, password):
    grades = pullGrades(username, password)
    return jsonify(grades)


@app.route("/gradesGraph/<username>/<password>", methods=["GET"])
def get_grades_graph(username, password):
    # Fetch the grades using the username and password
    grades_data = pullGrades(username, password)

    # Create a bar graph of the grades and get the binary image object
    image_obj = barGraph(grades_data)

    # Send the binary image object as the response
    return send_file(image_obj, mimetype="image/png")


@app.route("/assignments/<username>/<password>", methods=["GET"])
def get_assignments(username, password):
    assignments = pullAssignments(username, password)
    return jsonify(assignments)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
