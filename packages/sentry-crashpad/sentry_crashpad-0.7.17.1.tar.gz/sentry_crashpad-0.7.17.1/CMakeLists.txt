cmake_minimum_required(VERSION 3.16...3.31)
project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION})

message(STATUS "sentry-crashpad-wheel version: ${SKBUILD_PROJECT_VERSION}")
string(REGEX MATCH "^([0-9]+)\.([0-9]+)\.([0-9]+)" CRASHPAD_HANDLER_VERSION "${SKBUILD_PROJECT_VERSION}")
message(STATUS "crashpad_handler version: ${CRASHPAD_HANDLER_VERSION}")

find_package(sentry REQUIRED)

set(crashpad-handler-executable ${sentry_INCLUDE_DIRS}/../bin/crashpad_handler${CMAKE_EXECUTABLE_SUFFIX})
install(PROGRAMS ${crashpad-handler-executable} DESTINATION sentry_crashpad/data/bin)

if (WIN32)
    set(crashpad-wer-library ${sentry_INCLUDE_DIRS}/../bin/crashpad_wer${CMAKE_SHARED_LIBRARY_SUFFIX})
    install(FILES ${crashpad-wer-library} DESTINATION sentry_crashpad/data/bin)
endif ()
