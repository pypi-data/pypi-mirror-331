import sys

import osc.commandline_git


class LoginUpdateCommand(osc.commandline_git.GitObsCommand):
    """
    Update a Gitea credentials entry
    """

    name = "update"
    parent = "LoginCommand"

    def init_arguments(self):
        self.parser.add_argument("name")
        self.parser.add_argument("--new-name")
        self.parser.add_argument("--new-url")
        self.parser.add_argument("--new-user")
        self.parser.add_argument("--new-token")
        self.parser.add_argument("--new-ssh-key")
        self.parser.add_argument("--set-as-default", action="store_true")

    def run(self, args):
        print(f"Updating a Gitea credentials entry with name '{args.name}' ...", file=sys.stderr)
        print(f" * Config path: {self.gitea_conf.path}", file=sys.stderr)
        print("", file=sys.stderr)

        # TODO: try to authenticate to verify that the updated entry works

        original_login = self.gitea_conf.get_login(args.name)
        print("Original entry:")
        print(original_login.to_human_readable_string())

        updated_login = self.gitea_conf.update_login(
            args.name,
            new_name=args.new_name,
            new_url=args.new_url,
            new_user=args.new_user,
            new_token=args.new_token,
            new_ssh_key=args.new_ssh_key,
            set_as_default=args.set_as_default,
        )
        print("")
        print("Updated entry:")
        print(updated_login.to_human_readable_string())
