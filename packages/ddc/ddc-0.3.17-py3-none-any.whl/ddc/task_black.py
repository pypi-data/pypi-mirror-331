from ddc.utils import stream_exec_cmd, run_if_time_has_passed
import os


def start_black(cwd: str, subdir: str, lang: str):
    image_tag = "cr.yandex/crpm0p0gmosuerb6vnrp/pronto-black-{lang}".format(lang=lang)
    root = "/usr/app"

    def _pull():
        stream_exec_cmd("docker pull {image_tag}".format(image_tag=image_tag))

    run_if_time_has_passed("black-" + lang, 60, _pull)
    path = os.path.abspath(os.path.join(root, subdir)) if subdir else root
    cwd = os.path.abspath(os.path.join(cwd, subdir)) if subdir else root
    return stream_exec_cmd(
        "docker run --rm -v {cwd}:{path} {image_tag}".format(
            cwd=cwd, path=path, image_tag=image_tag
        )
    )
