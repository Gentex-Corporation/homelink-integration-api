FROM mcr.microsoft.com/devcontainers/python:3.14-bookworm

ARG USERNAME=vscode

RUN apt-get update -y \
	&& apt-get upgrade -y \
	&& apt-get install -y --no-install-recommends black

# Remember zsh history through container rebuilds
RUN mkdir /commandhistory && touch /commandhistory/.zsh_history && chown -R $USERNAME:$USERNAME /commandhistory

USER $USERNAME

# Configure ohmyzsh
RUN sed -i 's/"devcontainers"/"agnoster"/g' /home/$USERNAME/.zshrc

# Configure shell
RUN echo 'export PROMPT_COMMAND="history -a"' >> "/home/$USERNAME/.zshrc" && \
	echo 'export HISTFILE=/commandhistory/.zsh_history' >> "/home/$USERNAME/.zshrc" && \
	echo DEFAULT_USER=$USERNAME  >> "/home/$USERNAME/.zshrc" && \
	echo 'prompt_context(){}' >> "/home/$USERNAME/.zshrc"
