# MyNYT

mynyt is a library that accesses the publicly available RSS feeds of the New York Times and converts it to an easy-to-digest daily summary.

Most users of the New York Times appreciate a quick and easy way to access news every day in the morning.
However. they find it difficult to customize based on their individual needs and preferences.
By making a Python library, anyone can easily customize their own NYT summary.

## Features

- Collects news from different feeds of the NYT
- Processes and orders them, removing duplicates by title
- Converts it to a clean HTML
- Sends it to your email
- Allows for quick customization: feeds, emails, HTML, etc.

## Installation

To install MyNYT, use pip: ```pip install mynyt```.

However, many prefer to use a virtual environment.

MacOS / Linux:

```sh
# make your desired directory
mkdir /path/to/your/directory
cd /path/to/your/directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install mynyt
source .venv/bin/activate
pip install mynyt

deactivate
```

Windows CMD:

```sh
# make your desired directory
mkdir C:path\to\your\directory
cd C:path\to\your\directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install mynyt
.venv\Scripts\activate
pip install mynyt

deactivate
```

## Usage

The most basic features can be found in the examples, but you must setup the emailing yourself (tutorial below).

```python
from mynyt import MyNYT

if __name__ == '__main__':
    news = MyNYT(
        'your.email@gmail.com',
        'your appp pass word',
        rss_links = None,
        style_sheet = None
    )

    news.get_all_stories(
        rotate_through_feeds = True
    )

    news.remove_duplicates(
        all_stories = None,
    )

    news.trim_to_length(
        length = 12,
        stories = None
    )

    news.convert_news_to_html(
        stories = None,
        image_story_html_template = None,
        imageless_story_html_template = None,
        main_div_styles = None
    )

    news.send_email(
        recipient = 'your.email@gmail.com',
        main_subject = 'Daily NYT',
        timezone = 'US/Eastern',
        story_html_body = None,
        main_html_template = None
    )
```

## Email Configuration

Currently, there is only support for gmail. This library uses smtplib to send emails.
For it to work, the user will need to create an app password.

1) To create an app password, you need 2-Step Verification on your Google Account.

This can be through a variety of methods, whether it be through the Google Authenticator App, a secondary email, or a phone number

2) Create the app password

This link will direct you to your app passwords: https://myaccount.google.com/apppasswords.
They grant COMPLETE access to your account. If you do not have a Google Account or wish to use a different "junk" email, simply create a new google account.

Further help can be found here: https://support.google.com/mail/answer/185833?hl=en#:~:text=Important:%20To%20create%20an%20app,create%20a%20new%20app%20password.

## Automatic Execution

If you want a daily email with a snapshot of the NYT at a predetermined time, we have to use automation to make it happen.

## Crontab: MacOS / Linux ONLY

Because this library provides a news summary of the most recent events, you can use it with a Crontab.
Crontab is available on Unix devices and is not for Windows users.

The format of ```minute hour day-of-month month day-of-week command``` allows us to have the following command:

```x y * * * ...``` will run at y:x o' clock (e.g.: if x was 30 and y was 18, it would be at 6:30 PM)

If you would like to have a daily email at 7:00 AM to run main.py, you could have the following command:

```
0 7 * * * cd /home/path/to/your/directory && .venv/bin/python3 main.py
```

For people that want to have two emails a day (at 7AM and 4PM), simply edit the crontab:

```
0 7,15 * * * cd /home/path/to/your/directory && .venv/bin/python3 main.py
```

If you did not use a venv, simply replace ```.venv/bin/python3``` with your path to python, like ```/path/to/your/python3``` or just ```python3``` if it was added to your path..

Visit https://crontab.guru/ to learn more.

## Task Scheduler: Windows ONLY

Windows users must take a different approach with Task Scheduler.

Press Win + R, type taskschd.msc, and hit Enter.

Create a basic task and name it, choosing your preferred frequency (like daily). The start time can also be chosen, something like 7AM.
It will start a program, with the program ```C:\path\to\your\python.exe``` and argument ```C:\path\to\your\directory\main.py```.

Visit https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page to learn more.

### Basic Customization

There are many parameters that are easy to use as well as others that require a mentioning.

#### rss_links

The parameter rss_links can be changed for what you want your news to be about.
Feeds can be found here: https://www.nytimes.com/rss

#### recipient

If you created a new Google Account, you can have the email recipient be your main email like: ```main.email@other.com```
IMPORTANT: You may not use this feature to send emails to other parties or for commercial use because it breaks the NYTimes Terms of Service.

From the NYTimes:

"We allow the use of NYTimes.com RSS feeds for personal use in a news reader or as part of a non-commercial blog.
We require proper format and attribution whenever New York Times content is posted on your website, and we reserve the right to require that you cease distributing NYTimes.com content.
Please read the Terms and Conditions for complete instructions.
Commercial use of the Service is prohibited without prior written permission from NYT which may be requested via email to: nytlg-sales@nytimes.com."

#### Timezone

If your timezone is not ```US/Eastern```, you may change it to a different string that is a valid pytz timezone.
To find them:

```python
import pytz
print(pytz.all_timezones())
```

### Advanced Customization

Advanced customization can be added for your own personal taste.

#### style_sheet

The style sheet allows you to change the formatting and style of the email, like in regular HTML.

It is preset as this:

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: Verdana, sans-serif;
}

h1 {
    font-size: 15px;
}

p, div {
    font-size: 12px;
}
```

#### story_html_template

There are two templates for each story, one for ones with images and one for ones without images.

```html
<div style = 'display: flex; width: 100%; padding: 10px;'>
<div style = 'width: 70%; margin-right: 10px;'>
    <h3><a href='{link}'>{title}</a></h3>
    <p><br>
    {description}<br><br>
    {authors}<br>
    </p>
</div>
<div style = 'width: 30%;'>
    <img src = '{article_image_link}' alt = 'HTML Image' width = '100%'>
</div>
</div>
<hr style = 'margin-left: 10px; margin-right: 10px; width: calc(100% - 20px);'>
```

```html
<div style = 'width: 100%; padding: 10px;'>
    <div>
        <h3><a href='{link}'>{title}</a></h3>
        <p><br>
        {description}<br><br>
        {authors}<br>
        </p>
    </div>
</div>
<hr style = 'margin-left: 10px; margin-right: 10px; width: calc(100% - 20px);'>
```

Note that the brackets are placeholders for the ```.format()``` function that is handled by the internal method. All of those parameters must be included, and no more can be added.

#### main_html_template

Similar to the images, this is a template for the entire email.
The default is set to this:

```html
<!DOCTYPE html>
<html>
    <head>
        <style>
            {style_sheet}
        </style>
    </head>
    <body>
        <h1>
            Daily News Summary of the New York Times
        </h1>
        {html_body}
    </body>
</html>
```

The parameter ```html_body``` is what the stories are, each with their own paragraph headers.

## Disclaimer
This library, mynyt, retrieves publicly available news content via RSS feeds from the New York Times (NYT).
All news articles and content are owned by the New York Times and are subject to their Terms of Service.
By using this library, you agree to comply with the New York Times' Terms of Service and all relevant copyright laws.

The content provided by this library is intended for personal (like sending emails to yourself) and non-commercial use only.
Redistribution, modification, or commercial use of the content retrieved from NYT is prohibited unless explicitly allowed by the New York Times.

## License

The License is an MIT License found in the LICENSE file.