import vt


def scan_and_fetch_analysis_stats(file_path_list: list[str]):
    client = vt.Client('TOKEN')
    for path in file_path_list:
        with open(path, "rb") as f:
            print("scanning")
            analysis = client.scan_file(f, wait_for_completion=True)
            print("completed")
            f.close()
        completed_analysis = client.get_object(f"/analyses/{analysis.id}")
        with(open('analysis.txt', "a+")) as analysis_file:
            analysis_file.write(f"{path} {completed_analysis.stats}")
    client.close()
