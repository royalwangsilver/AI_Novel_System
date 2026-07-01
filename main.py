from ui.interface import create_interface


def main():
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
