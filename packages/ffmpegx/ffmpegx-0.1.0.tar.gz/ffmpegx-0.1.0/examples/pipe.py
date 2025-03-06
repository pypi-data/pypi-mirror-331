import ffmpegx


def main():
    stream1 = ffmpegx.input("input.mp4").copy().video()
    stream2 = ffmpegx.from_stream(stream1).output("output.mp4")
    stream2.run()


if __name__ == "__main__":
    main()
