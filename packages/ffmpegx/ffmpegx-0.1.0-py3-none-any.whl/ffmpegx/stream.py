import os
import subprocess


def input(input: str, format: str | None = None):
    return Stream().input(input, format)


def from_stream(stream: "Stream"):
    return Stream().from_stream(stream)


def seek(ss: str, to: str):
    return Stream().seek(ss, to)


def hwaccel(typ: str):
    return Stream().hwaccel(typ)


pipecount = 0


class Stream:
    def __init__(self, cmd="ffmpeg"):
        self.cmd = [cmd]
        self.__pipe_path: str | None = None

    def seek(self, ss: str, to: str):
        self.args("-ss", ss)
        self.args("-to", to)
        return self

    def hwaccel(self, typ: str):
        self.args("-hwaccel", typ)
        return self

    def input(self, input: str, format: str | None = None):
        if format is not None:
            self.args("-f", format)
        self.args("-i", input)
        return self

    def from_stream(self, stream: "Stream", format="mpegts"):
        stream.pipe(format=format)
        assert stream.__pipe_path is not None
        self.args("-i", stream.__pipe_path)
        return self

    def output(self, output: str, format: str | None = None):
        if format is not None:
            self.args("-f", format)
        self.args(output)
        return self

    def pipe(self, format: str = "mpegts"):
        global pipecount
        self.__pipe_path = f"/tmp/ffmpegx-pipe-{pipecount}"
        assert self.__pipe_path is not None
        if os.path.exists(self.__pipe_path):
            os.remove(self.__pipe_path)
        os.mkfifo(self.__pipe_path)
        pipecount += 1
        self.overwrite()
        self.args("-f", format)
        self.args(self.__pipe_path)
        subprocess.Popen(self.cmd)

    def copy(self):
        self.args("-c", "copy")
        return self

    def cv(self, typ: str):
        self.args("-c:v", typ)
        return self

    def cv_h264_nvenc(self):
        self.args("-c:v", "h264_nvenc")
        return self

    def ca(self, typ: str):
        self.args("-c:a", typ)
        return self

    def cs(self, typ: str):
        self.args("-c:s", typ)
        return self

    def map(self, arg: str):
        self.args("-map", arg)
        return self

    def vn(self):
        self.args("-vn")
        return self

    def an(self):
        self.args("-an")
        return self

    # alias of "-map a"
    def audio(self):
        return self.map("a")

    # alias of "-map v"
    def video(self):
        return self.map("v")

    # alias of "-map v"
    def subtitle(self):
        return self.map("s")

    def overwrite(self):
        self.args("-y")
        return self

    def args(self, *args: str):
        self.cmd.extend(args)

    def display(self):
        print(" ".join(self.cmd))
        return self

    def run(self):
        subprocess.run(self.cmd)
