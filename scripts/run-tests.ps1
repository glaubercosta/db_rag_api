# Test Runner PowerShell Script for Windows

param(
    [string]$Action = "help",
    [string]$File = "",
    [string]$Pattern = ""
)

function Show-Help {
    Write-Host "Test Runner Commands:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  .\run-tests.ps1 install-deps     - Install test dependencies" -ForegroundColor Yellow
    Write-Host "  .\run-tests.ps1 test             - Run all tests" -ForegroundColor Yellow
    Write-Host "  .\run-tests.ps1 test-unit        - Run unit tests only" -ForegroundColor Yellow
    Write-Host "  .\run-tests.ps1 test-integration - Run integration tests only" -ForegroundColor Yellow
    Write-Host "  .\run-tests.ps1 test-security    - Run security tests only" -ForegroundColor Yellow
    Write-Host "  .\run-tests.ps1 test-performance - Run performance tests only" -ForegroundColor Yellow
    Write-Host "  .\run-tests.ps1 test-fast        - Run fast tests (exclude slow)" -ForegroundColor Yellow
    Write-Host "  .\run-tests.ps1 test-coverage    - Run tests with coverage" -ForegroundColor Yellow
    Write-Host "  .\run-tests.ps1 test-parallel    - Run tests in parallel" -ForegroundColor Yellow
    Write-Host "  .\run-tests.ps1 clean            - Clean test artifacts" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\run-tests.ps1 test-file -File 'tests\unit\test_database_scanner.py'" -ForegroundColor Gray
    Write-Host "  .\run-tests.ps1 test-pattern -Pattern 'sql_injection'" -ForegroundColor Gray
}

switch ($Action) {
    "install-deps" {
        Write-Host "Installing test dependencies..." -ForegroundColor Green
        pip install pytest pytest-cov pytest-xdist pytest-mock coverage pytest-html
    }
    
    "test" {
        Write-Host "Running all tests..." -ForegroundColor Green
        pytest tests\ -v
    }
    
    "test-unit" {
        Write-Host "Running unit tests..." -ForegroundColor Green
        pytest tests\unit\ -v -m unit
    }
    
    "test-integration" {
        Write-Host "Running integration tests..." -ForegroundColor Green
        pytest tests\integration\ -v -m integration
    }
    
    "test-security" {
        Write-Host "Running security tests..." -ForegroundColor Green
        pytest tests\security\ -v -m security
    }
    
    "test-performance" {
        Write-Host "Running performance tests..." -ForegroundColor Green
        pytest tests\performance\ -v -m "performance and slow"
    }
    
    "test-fast" {
        Write-Host "Running fast tests..." -ForegroundColor Green
        pytest tests\ -v -m "not slow"
    }
    
    "test-coverage" {
        Write-Host "Running tests with coverage..." -ForegroundColor Green
        pytest tests\ --cov=. --cov-report=html --cov-report=term-missing
        Write-Host "Coverage report generated in htmlcov\index.html" -ForegroundColor Cyan
    }
    
    "test-parallel" {
        Write-Host "Running tests in parallel..." -ForegroundColor Green
        pytest tests\ -v -n auto
    }
    
    "test-file" {
        if ($File -eq "") {
            Write-Host "Error: File parameter required" -ForegroundColor Red
            Write-Host "Usage: .\run-tests.ps1 test-file -File 'path\to\test_file.py'" -ForegroundColor Yellow
            exit 1
        }
        Write-Host "Running tests in file: $File" -ForegroundColor Green
        pytest $File -v
    }
    
    "test-pattern" {
        if ($Pattern -eq "") {
            Write-Host "Error: Pattern parameter required" -ForegroundColor Red
            Write-Host "Usage: .\run-tests.ps1 test-pattern -Pattern 'test_name_pattern'" -ForegroundColor Yellow
            exit 1
        }
        Write-Host "Running tests matching pattern: $Pattern" -ForegroundColor Green
        pytest tests\ -v -k $Pattern
    }
    
    "test-openai" {
        Write-Host "Running tests that require OpenAI..." -ForegroundColor Green
        pytest tests\ -v -m requires_openai
    }
    
    "test-database" {
        Write-Host "Running tests that require database..." -ForegroundColor Green
        pytest tests\ -v -m requires_database
    }
    
    "clean" {
        Write-Host "Cleaning test artifacts..." -ForegroundColor Green
        if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
        if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
        if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
        if (Test-Path "test_report.html") { Remove-Item -Force "test_report.html" }
        
        # Remove Python cache files
        Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force
        Get-ChildItem -Recurse -Name "__pycache__" -Directory | Remove-Item -Recurse -Force
        
        Write-Host "Test artifacts cleaned" -ForegroundColor Green
    }
    
    "report" {
        Write-Host "Generating test report..." -ForegroundColor Green
        pytest tests\ --html=test_report.html --self-contained-html
        Write-Host "Test report generated: test_report.html" -ForegroundColor Cyan
    }
    
    "quality" {
        Write-Host "Running quality checks..." -ForegroundColor Green
        Write-Host "Linting tests..." -ForegroundColor Yellow
        flake8 tests\
        Write-Host "Running tests with coverage..." -ForegroundColor Yellow
        pytest tests\ --cov=. --cov-report=html --cov-report=term-missing
    }
    
    default {
        Show-Help
    }
}
