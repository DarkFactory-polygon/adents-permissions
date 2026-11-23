def rec(agent="build-bot", resource="repo/app", action="read", by="alice", until="2099-01-01"):
    return (
        f"  - {{agent: {agent}, resource: {resource}, action: {action}, "
        f"granted_by: {by}, until: {until}}}\n"
    )


def write(tmp_path, *records):
    (tmp_path / "permissions.yaml").write_text("permissions:\n" + "".join(records))
