class TokenStorage:
    def save(self, ctx, file: str):
        with open(f"io/output/{file}.txt", "a", encoding="utf-8") as f:
            f.write(f"{ctx.email}:{ctx.password}:{ctx.token}\n")
            