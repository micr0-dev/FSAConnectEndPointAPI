# FSAConnectEndPointAPI

## Description

This project allows users to fetch their grades from the Fulton Science Academy Connect. It's designed with efficiency in mind and implements a caching mechanism to improve response times.

## Usage

This project can be accessed through simple web URLs according to your preference:

### JavaScript Embedded Widget
To embed a JavaScript widget displaying the grades, use the following URL:
```
https://micr0.dev/gradesEmbed/<username>/<password>
```
![Screenshot from 2023-08-12 12-01-37](https://github.com/MiraslauKavaliou/FSAConnectEndPointAPI/assets/26364458/e913e68e-fbb1-4ddb-989f-550ff0a97ed1)

### Basic Image Embed (legacy)
To embed an image that shows a graph of the grades, use the following URL:
```
https://micr0.dev/gradesGraph/<username>/<password>
```
![image](https://github.com/MiraslauKavaliou/FSAConnectEndPointAPI/assets/26364458/394edad7-11af-410a-a1c1-2cee40795684)

### JSON of Your Grades
To retrieve a JSON representation of the grades, use the following URL:
```
https://micr0.dev/grades/<username>/<password>
```
Replace `<username>` and `<password>` with the appropriate login credentials for Fulton Science Academy.

## Features

- **Privacy Focused**: This project is built with privacy as a top priority. Please see the Privacy section below for details.
- **Fast Retrieval**: Utilizes caching to store grades for up to 10 minutes, reducing wait times for frequently accessed data.
- **Ease of Use**: Simple and intuitive interface to pull grades with minimal input.

## Privacy

### 🚨 Important Privacy Information 🚨

- **No Storage of Login Credentials**: Your login data, including username and password, is not stored on the server. It's only used to authenticate with the Fulton Science Academy portal and is discarded immediately after use.
- **Cached Grades**: To improve efficiency, grades may be stored in a cache for up to 10 minutes. After this time, the cached data is deleted, and new data is fetched from the server. This cache is managed securely and designed with user privacy in mind.

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcomed.

## License

This project is licensed under the GNU General Public License v3.0. This ensures that the software is free to use, modify, and distribute, and that any derivative works are also under the same license.

Please see the [LICENSE](LICENSE) file in the project's repository for the full text of the license, or you can [read it online here](https://www.gnu.org/licenses/gpl-3.0.en.html).
