import vt
from vt import APIError


def scan_and_fetch_analysis_stats(path, sha):
    client = vt.Client('TOKEN')
    try:
        file_info = client.get_object(
            f"/files/{sha}")
        return
    except APIError:
        print("file does not exist")
    with open(path, "rb") as f:
        print("scanning")
        analysis = client.scan_file(f, wait_for_completion=True)
        print("completed")
        f.close()
    completed_analysis = client.get_object(f"/analyses/{analysis.id}")
    with(open("analysis.txt", "a+")) as analysis_file:
        analysis_file.write(f"{path} {completed_analysis.stats}")
    client.close()
