FROM python:3.14

ENV TZ=Asia/Kolkata

RUN apt-get update && \
    apt-get install -y tzdata curl && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get clean

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser

# Give ownership of the application
RUN chown -R appuser:appuser /app

# Create uploads directory
RUN mkdir -p /app/app/uploads && \
    chown -R appuser:appuser /app/app/uploads

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
CMD curl --fail http://localhost:5000/health || exit 1

CMD ["gunicorn", "-w", "4", "--timeout", "300", "-b", "0.0.0.0:5000", "run:app"]