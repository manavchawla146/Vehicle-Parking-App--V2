@echo off
echo 🚀 Cache Management Commands
echo ============================
echo.
echo Available commands:
echo   cache-status    - Show cache status
echo   cache-keys      - Show all cache keys
echo   cache-stats     - Show Redis statistics  
echo   cache-test      - Run performance tests
echo   cache-clear     - Clear all cache
echo   cache-monitor   - Real-time monitoring
echo   cache-full      - Run comprehensive test
echo.
echo Examples:
echo   cache-status
echo   cache-test
echo   cache-keys
echo.

if "%1"=="status" goto status
if "%1"=="keys" goto keys
if "%1"=="stats" goto stats
if "%1"=="test" goto test
if "%1"=="clear" goto clear
if "%1"=="monitor" goto monitor
if "%1"=="full" goto full

echo ❌ Unknown command: %1
echo Use: cache-status, cache-keys, cache-stats, cache-test, cache-clear, cache-monitor, cache-full
goto end

:status
echo 📊 Checking cache status...
python cache_cli.py status
goto end

:keys
echo 🗂️  Showing cache keys...
python cache_cli.py keys
goto end

:stats
echo 📈 Showing Redis statistics...
python cache_cli.py stats
goto end

:test
echo 🧪 Running performance tests...
python cache_cli.py test
goto end

:clear
echo 🗑️  Clearing cache...
python cache_cli.py clear
goto end

:monitor
echo 👀 Starting real-time monitoring...
python cache_cli.py monitor
goto end

:full
echo 🚀 Running comprehensive cache test...
python cache_monitor.py
goto end

:end
echo.
echo ✅ Command completed! 