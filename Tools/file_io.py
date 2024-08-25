from datetime import datetime


def save_markdown(task_output):
    # Get today's date in the format YYYY-MM-DD
    today_date = datetime.now().strftime('%Y-%m-%d')
    # Set the filename with today's date
    filename = f"Trabajos {today_date}.md"
    # Write the task output to the markdown file
    with open(filename, 'w', encoding="utf-8") as file:
        file.write(task_output.raw_output)
    print(f"File saved as {filename}")