FROM python:3.9-slim

RUN useradd -ms /bin/bash bot_user

USER bot_user

WORKDIR /home/bot_user

ENV PATH="/home/bot_user/.local/bin:${PATH}"

COPY --chown=bot_user:bot_user requirements.txt requirements.txt

RUN pip install --disable-pip-version-check --user -r requirements.txt

COPY --chown=bot_user:bot_user . .

CMD ["python", "bot.py"]
