import time
import logging
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
import os
import threading
from ddc.utils import (
    write_ddc_file,
    get_path_ddc_file,
    exec_cmd_with_stream_output,
)

META_DOCKER_COMPOSE_FILENAME = "meta-docker-compose_{port}.yaml"

ACTUAL_DOCKER_COMPOSE_FILE = """
version: '3'
services:
  redis:
    image: redis:alpine
  meta:
    image: {docker_image}
    depends_on:
      - redis
    ports:
      - "{port}:8080"
    volumes:
      - ~/.rwmeta:/root/.rwmeta:delegated
      - ./meta_conf:/root/meta_conf:delegated
      - ./:/root/workspace/production:delegated
    environment:
      JAVA_OPTS: -Duser.timezone=Europe/Moscow -Xms1000m -Xmx2500m -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=9010 -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=localhost
      META_CONFIG: /root/meta_conf/meta-loc-dev.yaml
      RELEASE_VERSION2: dev
      RELEASE_VERSION: local_dev
      META_APP_CONTENT_CONFIG_DIR: /root/meta_conf
      META_APP_CONTENT_WORKSPACE_DIR: /root/workspace
"""  # noqa


class GitAddEventHandler(RegexMatchingEventHandler):
    IMAGES_REGEX = [r".*\.html"]

    def __init__(self):
        super().__init__(regexes=self.IMAGES_REGEX)

    def on_moved(self, event):
        super(GitAddEventHandler, self).on_moved(event)

        self.__git_add_file(event.src_path)

    def on_created(self, event):
        super(GitAddEventHandler, self).on_created(event)
        self.__git_add_file(event.src_path)

    def __git_add_file(self, file_path: str):
        if file_path.endswith(".html"):
            os.system("git add " + file_path)
            logging.info("git add = %s" % str(file_path))


def start_add_file_watchdog(path):
    logging.info("Start new html files watchdog")

    event_handler = GitAddEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


class AddFilesThread(threading.Thread):
    def __init__(self, path):
        threading.Thread.__init__(self)
        self.path = path

    def run(self):
        start_add_file_watchdog(self.path)


def start_meta(cwd, port, docker_image, auto_git_add):
    if auto_git_add:
        AddFilesThread(cwd).start()

    compose_filename = META_DOCKER_COMPOSE_FILENAME.format(port=port)
    compose_full_file_path = get_path_ddc_file(compose_filename)
    target_compose_content = ACTUAL_DOCKER_COMPOSE_FILE.format(
        port=port, docker_image=docker_image
    )
    write_ddc_file(compose_filename, target_compose_content)

    compose_base_cmd_base = [
        "docker",
        "compose",
        "-f",
        "{compose_full_file_path}".format(compose_full_file_path=compose_full_file_path),
        "-p",
        "ddc_meta_{port}".format(port=port),
        "--project-directory={cwd}".format(cwd=cwd)
    ]

    exec_cmd_with_stream_output(compose_base_cmd_base + ["down"])
    try:
        exec_cmd_with_stream_output(compose_base_cmd_base + ["pull"])
        exec_cmd_with_stream_output(compose_base_cmd_base + ["up"])
    finally:
        exec_cmd_with_stream_output(compose_base_cmd_base + ["down"])
