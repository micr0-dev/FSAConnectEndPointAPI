from io import BytesIO
from re import search
from requests import Session
from bs4 import BeautifulSoup as bs
from string import digits
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import pandas as pd
import time
from functools import lru_cache
from datetime import datetime, timedelta
import plotly.graph_objects as go


class timed_lru_cache:
    def __init__(self, maxsize=100, ttl=300):
        self.cache = {}
        self.maxsize = maxsize
        self.ttl = ttl  # time to live in seconds

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            key = (args, tuple(kwargs.items()))
            # Check if the cache is full
            if len(self.cache) >= self.maxsize:
                self.cache.pop(next(iter(self.cache)))
            # Check for cached result and ttl
            if key in self.cache:
                result, timestamp = self.cache[key]
                if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                    return result
            # Compute and cache the result
            result = func(*args, **kwargs)
            self.cache[key] = (result, datetime.now())
            return result

        return wrapper


@timed_lru_cache(maxsize=4, ttl=600)  # Cache for 10 minutes
def pullGrades(username: str, password: str) -> dict:
    """
    Pull the grades for the given username and password.

    :param username: username of user to pull from
    :param password: password of user to pull from
    :return: dictionary of grades where the key is string course and the value is float grade
    """

    # start_time = time.time()

    # print("logging in..")
    with Session() as s:
        # site_start_time = time.time()

        site = s.get("https://fultonscienceacademy.radixlms.com/login/")
        # print(f"Getting the site took {time.time() - site_start_time} seconds")
        bs_content = bs(site.content, "html.parser")
        token = bs_content.find("input", {"name": "logintoken"})["value"]
        login_data = {
            "username": username,
            "password": password,
            "logintoken": token,
            "anchor": "",
        }
        # post_start_time = time.time()
        s.post("https://fultonscienceacademy.radixlms.com/login/index.php", login_data)
        # print(f"Posting the site took {time.time() - post_start_time} seconds")
        grade_page = s.get(
            "https://fultonscienceacademy.radixlms.com/grade/report/overview/"
        )
        # print(f"Fetching login page took {time.time() - site_start_time} seconds")

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

    # end_time = time.time()
    # print(f"pullGrades took {end_time - start_time} seconds in total")

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


from flask import Flask, jsonify, send_file, render_template_string

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


@app.route("/gradesEmbed/<username>/<password>", methods=["GET"])
def get_grades_embed(username, password):
    # Example: Create a DataFrame with sample grades data
    # Replace this with the actual logic to retrieve grades
    # df = pd.DataFrame(
    #     {
    #         "Subject": ["Math", "Science", "History", "English"],
    #         "Grades": [90, 85, 78, 88],
    #     }
    # )

    grades_dict = pullGrades(username, password)

    # Create a DataFrame from the grades dictionary
    df = pd.DataFrame(list(grades_dict.items()), columns=["Subject", "Grades"])

    # Create a Plotly figure using the DataFrame
    fig = px.bar(df, x="Subject", y="Grades", title="Your Grades")

    # Round the grades and add them as text annotations on top of the bars
    for index, row in df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row["Subject"]],
                y=[row["Grades"]] + [5],
                text=[str(int(round(row["Grades"])))],
                mode="text",
                showlegend=False,
            )
        )

    # Convert the Plotly figure to HTML
    graph_html = pio.to_html(fig, include_plotlyjs="cdn", full_html=False)

    # Define the HTML to be embedded
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Grades Widget</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
            .graph {{
                width: 100%;
                height: 100%;
            }}
        </style>
    </head>
    <body>
        <div class="graph">
            {graph_html}
        </div>
    </body>
    </html>
    """

    return render_template_string(html)


@app.route("/assignments/<username>/<password>", methods=["GET"])
def get_assignments(username, password):
    assignments = pullAssignments(username, password)
    return jsonify(assignments)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
