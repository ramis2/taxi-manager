@echo off
chcp 65001 > nul
title Taxi Manager System
color 0A

:menu
cls
echo ========================================
echo        TAXI MANAGER SYSTEM
echo ========================================
echo 1. Dashboard
echo 2. Add New Driver
echo 3. Add New Car
echo 4. View All Drivers
echo 5. View All Cars
echo 6. Generate Driver Letter
echo 7. View Reports
echo 8. Exit
echo ========================================
set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto dashboard
if "%choice%"=="2" goto add_driver
if "%choice%"=="3" goto add_car
if "%choice%"=="4" goto view_drivers
if "%choice%"=="5" goto view_cars
if "%choice%"=="6" goto generate_letter
if "%choice%"=="7" goto reports
if "%choice%"=="8" goto exit
echo Invalid choice! Press Enter to try again.
pause
goto menu

:dashboard
cls
echo ========================================
echo            DASHBOARD
echo ========================================

:: Check if data files exist and count entries
set driver_count=0
if exist drivers.txt (
    for /f %%a in ('type drivers.txt ^| find /c /v ""') do set driver_count=%%a
)

set car_count=0
if exist cars.txt (
    for /f %%a in ('type cars.txt ^| find /c /v ""') do set car_count=%%a
)

set letter_count=0
if exist letters.txt (
    for /f %%a in ('type letters.txt ^| find /c /v ""') do set letter_count=%%a
)

echo Total Drivers: %driver_count%
echo Total Cars: %car_count%
echo Letters Generated: %letter_count%
echo ========================================

echo.
echo RECENT DRIVERS:
echo --------------
if exist drivers.txt (
    echo Reading drivers data...
    set count=0
    for /f "tokens=1-4 delims=," %%a in (drivers.txt) do (
        set /a count+=1
        set "driver_!count!_name=%%a"
        set "driver_!count!_license=%%b"
        set "driver_!count!_phone=%%c"
        set "driver_!count!_status=%%d"
    )
    
    if %count% gtr 0 (
        set /a start=%count%-4
        if %start% lss 1 set start=1
        for /l %%i in (%start%,1,%count%) do (
            call echo - %%driver_%%i_name%% ^(License: %%driver_%%i_license%%, Phone: %%driver_%%i_phone%%^)
        )
    ) else (
        echo No drivers found
    )
) else (
    echo No drivers data file
)

echo.
echo RECENT CARS:
echo -------------
if exist cars.txt (
    echo Reading cars data...
    set count=0
    for /f "tokens=1-4 delims=," %%a in (cars.txt) do (
        set /a count+=1
        set "car_!count!_model=%%a"
        set "car_!count!_cpnc=%%b"
        set "car_!count!_plate=%%c"
        set "car_!count!_status=%%d"
    )
    
    if %count% gtr 0 (
        set /a start=%count%-4
        if %start% lss 1 set start=1
        for /l %%i in (%start%,1,%count%) do (
            call echo - %%car_%%i_model%% ^(CPNC: %%car_%%i_cpnc%%, Plate: %%car_%%i_plate%%^)
        )
    ) else (
        echo No cars found
    )
) else (
    echo No cars data file
)

echo.
pause
goto menu

:add_driver
cls
echo ========================================
echo         ADD NEW DRIVER
echo ========================================
set /p name="Driver Name: "
set /p license="License Number: "
set /p phone="Phone Number: "
set /p email="Email (optional): "
set /p address="Address (optional): "

:: Validate required fields
if "%name%"=="" (
    echo Error: Name is required!
    pause
    goto add_driver
)
if "%license%"=="" (
    echo Error: License is required!
    pause
    goto add_driver
)
if "%phone%"=="" (
    echo Error: Phone is required!
    pause
    goto add_driver
)

:: Check if license already exists
set duplicate=0
if exist drivers.txt (
    findstr /i "%license%" drivers.txt > nul && set duplicate=1
)

if %duplicate% equ 1 (
    echo Error: Driver with license %license% already exists!
    pause
    goto add_driver
)

:: Save driver to file
echo %name%,%license%,%phone%,%email%,%address%,active,%date% %time% >> drivers.txt
echo.
echo SUCCESS: Driver %name% added successfully!
echo.
pause
goto menu

:add_car
cls
echo ========================================
echo          ADD NEW CAR
echo ========================================
set /p model="Car Model (e.g., Ford): "
set /p make="Make (e.g., Focus): "
set /p cpnc="CPNC Number: "
set /p plate="Plate Number: "
set /p year="Year: "
set /p color="Color: "

:: Validate required fields
if "%model%"=="" (
    echo Error: Model is required!
    pause
    goto add_car
)
if "%cpnc%"=="" (
    echo Error: CPNC is required!
    pause
    goto add_car
)
if "%plate%"=="" (
    echo Error: Plate is required!
    pause
    goto add_car
)

:: Check if CPNC or Plate already exists
set duplicate=0
if exist cars.txt (
    findstr /i "%cpnc%" cars.txt > nul && set duplicate=1
    findstr /i "%plate%" cars.txt > nul && set duplicate=1
)

if %duplicate% equ 1 (
    echo Error: Car with CPNC %cpnc% or Plate %plate% already exists!
    pause
    goto add_car
)

:: Save car to file
echo %model%,%make%,%cpnc%,%plate%,%year%,%color%,available,%date% %time% >> cars.txt
echo.
echo SUCCESS: Car %plate% added successfully!
echo.
pause
goto menu

:view_drivers
cls
echo ========================================
echo          ALL DRIVERS
echo ========================================
echo.

if not exist drivers.txt (
    echo No drivers found. Data file doesn't exist.
    echo.
    pause
    goto menu
)

type drivers.txt | find /c /v "" > nul || (
    echo No drivers found in database.
    echo.
    pause
    goto menu
)

echo ID  Name                License     Phone           Status
echo --- ------------------- ----------- --------------- -------
set counter=0
for /f "tokens=1-7 delims=," %%a in (drivers.txt) do (
    set /a counter+=1
    
    :: Truncate long names
    set "name=%%a"
    if "!name:~20!" neq "" set "name=!name:~0,17!..."
    
    :: Truncate other fields
    set "license=%%b"
    if "!license:~10!" neq "" set "license=!license:~0,9!.."
    
    set "phone=%%c"
    if "!phone:~12!" neq "" set "phone=!phone:~0,11!.."
    
    set "status=%%f"
    
    echo !counter!   !name!  !license!  !phone!  !status!
)

echo.
echo Total Drivers: %counter%
echo.
pause
goto menu

:view_cars
cls
echo ========================================
echo           ALL CARS
echo ========================================
echo.

if not exist cars.txt (
    echo No cars found. Data file doesn't exist.
    echo.
    pause
    goto menu
)

type cars.txt | find /c /v "" > nul || (
    echo No cars found in database.
    echo.
    pause
    goto menu
)

echo ID  Model      CPNC        Plate       Status
echo --- ---------- ----------- ----------- ----------
set counter=0
for /f "tokens=1-8 delims=," %%a in (cars.txt) do (
    set /a counter+=1
    
    :: Truncate fields
    set "model=%%a"
    if "!model:~9!" neq "" set "model=!model:~0,8!.."
    
    set "cpnc=%%c"
    if "!cpnc:~10!" neq "" set "cpnc=!cpnc:~0,9!.."
    
    set "plate=%%d"
    if "!plate:~10!" neq "" set "plate=!plate:~0,9!.."
    
    set "status=%%g"
    
    echo !counter!   !model!  !cpnc!  !plate!  !status!
)

echo.
echo Total Cars: %counter%
echo.
pause
goto menu

:generate_letter
cls
echo ========================================
echo      GENERATE DRIVER LETTER
echo ========================================
echo.

if not exist drivers.txt (
    echo No drivers found. Please add drivers first.
    echo.
    pause
    goto menu
)

:: Display drivers for selection
echo Available Drivers:
echo ------------------
set counter=0
for /f "tokens=1-3 delims=," %%a in (drivers.txt) do (
    set /a counter+=1
    set "driver_!counter!_name=%%a"
    set "driver_!counter!_license=%%b"
    echo !counter!. %%a (License: %%b)
)

echo.
set /p driver_num="Select driver number (1-%counter%): "

if %driver_num% lss 1 (
    echo Invalid selection!
    pause
    goto generate_letter
)
if %driver_num% gtr %counter% (
    echo Invalid selection!
    pause
    goto generate_letter
)

:: Get driver details
call set "driver_name=%%driver_%driver_num%_name%%"
call set "driver_license=%%driver_%driver_num%_license%%"

echo.
echo Letter Types:
echo 1. Employment Verification
echo 2. Warning Letter
echo 3. Appreciation Letter
echo 4. Salary Certificate
echo.
set /p letter_type="Select letter type (1-4): "

if "%letter_type%"=="1" set "type_name=Employment Verification"
if "%letter_type%"=="2" set "type_name=Warning Letter"
if "%letter_type%"=="3" set "type_name=Appreciation Letter"
if "%letter_type%"=="4" set "type_name=Salary Certificate"
if not defined type_name set "type_name=General Letter"

echo.
set /p letter_date="Letter Date (DD/MM/YYYY): "
if "%letter_date%"=="" set "letter_date=%date%"

:: Generate letter content
set "letter_content=TO WHOM IT MAY CONCERN"
set "letter_content=%letter_content%^&echo.^&echo."
set "letter_content=%letter_content%This is to certify that %driver_name% (License: %driver_license%)"
set "letter_content=%letter_content% is a registered driver with our taxi company."
set "letter_content=%letter_content%^&echo.^&echo."
set "letter_content=%letter_content%All necessary documents and licenses are verified and up to date."
set "letter_content=%letter_content%^&echo.^&echo."
set "letter_content=%letter_content%For any further information, please contact our office."
set "letter_content=%letter_content%^&echo.^&echo."
set "letter_content=%letter_content%Sincerely,^&echo.Taxi Manager^&echo.%letter_date%"

:: Save letter to file
echo %driver_name%,%driver_license%,%type_name%,%letter_date% >> letters.txt

:: Create letter file
set "filename=letter_%driver_name%_%date:/=_%_%time::=_%.txt"
set "filename=%filename: =_%"
(
echo TO WHOM IT MAY CONCERN
echo.
echo This is to certify that %driver_name% (License: %driver_license%)
echo is a registered driver with our taxi company.
echo.
echo All necessary documents and licenses are verified and up to date.
echo.
echo For any further information, please contact our office.
echo.
echo Sincerely,
echo Taxi Manager
echo %letter_date%
) > "%filename%"

echo.
echo SUCCESS: Letter generated and saved as "%filename%"
echo.
echo Letter Preview:
echo ===============
type "%filename%"
echo.
pause
goto menu

:reports
cls
echo ========================================
echo             REPORTS
echo ========================================
echo.
echo 1. Driver List Report
echo 2. Car List Report
echo 3. Letters Report
echo 4. Back to Main Menu
echo.
set /p report_choice="Select report type (1-4): "

if "%report_choice%"=="1" goto driver_report
if "%report_choice%"=="2" goto car_report
if "%report_choice%"=="3" goto letter_report
if "%report_choice%"=="4" goto menu

echo Invalid choice!
pause
goto reports

:driver_report
cls
echo ========================================
echo        DRIVER LIST REPORT
echo ========================================
echo Generated on: %date% %time%
echo ========================================
echo.

if exist drivers.txt (
    echo Total Drivers: 
    for /f %%a in ('type drivers.txt ^| find /c /v ""') do echo %%a
    echo.
    echo Name,License,Phone,Email,Address,Status,Added Date
    echo ---------------------------------------------------
    type drivers.txt
) else (
    echo No drivers data available.
)

echo.
echo ========================================
echo End of Report
echo.
pause
goto reports

:car_report
cls
echo ========================================
echo         CAR LIST REPORT
echo ========================================
echo Generated on: %date% %time%
echo ========================================
echo.

if exist cars.txt (
    echo Total Cars: 
    for /f %%a in ('type cars.txt ^| find /c /v ""') do echo %%a
    echo.
    echo Model,Make,CPNC,Plate,Year,Color,Status,Added Date
    echo ---------------------------------------------------
    type cars.txt
) else (
    echo No cars data available.
)

echo.
echo ========================================
echo End of Report
echo.
pause
goto reports

:letter_report
cls
echo ========================================
echo      LETTERS GENERATED REPORT
echo ========================================
echo Generated on: %date% %time%
echo ========================================
echo.

if exist letters.txt (
    echo Total Letters Generated: 
    for /f %%a in ('type letters.txt ^| find /c /v ""') do echo %%a
    echo.
    echo Driver Name,License,Letter Type,Date
    echo ------------------------------------
    type letters.txt
) else (
    echo No letters have been generated yet.
)

echo.
echo ========================================
echo End of Report
echo.
pause
goto reports

:exit
cls
echo ========================================
echo    Thank you for using Taxi Manager!
echo ========================================
echo.
echo Data Files Created:
if exist drivers.txt echo - drivers.txt
if exist cars.txt echo - cars.txt
if exist letters.txt echo - letters.txt
echo.
echo Press any key to exit...
pause > nul
exit
