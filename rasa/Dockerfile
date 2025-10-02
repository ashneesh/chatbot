FROM rasa/rasa:3.6.15


# Set working directory
WORKDIR /app

USER root
# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy Rasa files
COPY . .

# Set user
USER 1001

# Train the model on build (optional)
# RUN rasa train

# Expose port
EXPOSE 5005

# # Default command
# CMD ["rasa", "run", "--enable-api", "--cors", "*", "--debug"]
# Make Rasa look inside the `data` folder for domain, stories, rules, and NLU
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--debug", "--domain", "/app/data/domain.yml", "--model", "/models"]