FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
ENV VNC_PORT=5901
ENV NOVNC_PORT=6901
ENV MCP_PORT=8831

# Base deps + VNC + noVNC + Chromium system libs
RUN apt-get update && apt-get install -y \
    x11vnc xvfb \
    novnc websockify \
    curl ca-certificates \
    fonts-liberation libatk-bridge2.0-0 libatk1.0-0 libcups2 \
    libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libxcomposite1 \
    libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Node.js 22 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @playwright/mcp@latest \
    && npx playwright install chromium --with-deps

# noVNC startup wrapper
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 5901 6901 8831
CMD ["/start.sh"]
