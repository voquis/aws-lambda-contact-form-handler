# Stage 1
#   Local development image that also produces final build
#   to optionally be used in next stage.
#   To only use this stage, use --taget dev when building
FROM python:3-slim AS dev

RUN apt-get update
RUN apt-get upgrade

RUN apt-get install -y \
  zip

ENV USERNAME=lambda

# Create new user for root-less installs
RUN useradd --create-home ${USERNAME}

# Create python user directories for root-less installs
RUN mkdir -p /.local && chown -R ${USERNAME}:${USERNAME} /.local
RUN mkdir -p /.cache/pip && chown -R ${USERNAME}:${USERNAME} /.cache/pip

# Add python bin path to system path
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Create workdir and give user permissions
RUN mkdir -p /project/lambda
RUN chown -R ${USERNAME}:${USERNAME} /project

WORKDIR /project

# Copy project files
COPY --chown=${USERNAME}:${USERNAME} . .
RUN chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

# Switch to user
USER ${USERNAME}

RUN ./scripts/poetry.sh
RUN cd lambda && ../scripts/validate.sh
RUN cd lambda && ../scripts/build.sh

# Override entrypoint
ENTRYPOINT [ "bash" ]

# Stage 2
#   Copy and install wheel from previous stage
#   to build a final production-ready image
FROM public.ecr.aws/lambda/python:3

COPY --from=dev /project/lambda/dist/*.whl .
COPY --from=dev /project/lambda/app.py .

RUN pip install *.whl

CMD [ "app.handler" ]
