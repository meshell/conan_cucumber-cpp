# required minimum version of cmake
cmake_minimum_required(VERSION 3.2 FATAL_ERROR)

option(USE_STATIC_BOOST "Statically link Boost" ${WIN32})

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
set(CONAN_SYSTEM_INCLUDES ON)
conan_basic_setup()

# Check for clang compiler
if(CMAKE_CXX_COMPILER MATCHES ".*clang")
    set(CMAKE_COMPILER_IS_CLANGCXX 1)
endif()

############################################
# Create a single feature test executable. #
############################################
#
# cucumber-cpp
#

find_package(Cuke REQUIRED)

function(register_feature_steps STEP_DEFINITION_FILE)
    get_filename_component(STEP_DEFINITION_FILE_NAME ${STEP_DEFINITION_FILE} NAME)
    message(STATUS "Adding " ${STEP_DEFINITION_FILE})
    # In order to generate step definitions from multiple source files
    # we need to use set CUKE_OBJECT_PREFIX variable for every
    # source file to compile
    # https://github.com/cucumber/cucumber-cpp/issues/36
    string(REPLACE "-" "" OBJ_PREFIX ${STEP_DEFINITION_FILE_NAME})
    set_source_files_properties(${STEP_DEFINITION_FILE}.cpp PROPERTIES COMPILE_FLAGS "-DCUKE_OBJECT_PREFIX=Obj${OBJ_PREFIX}")
    set(STEP_SOURCES ${STEP_SOURCES} ${STEP_DEFINITION_FILE}.cpp PARENT_SCOPE)
endfunction()

if(CUKE_FOUND)
    register_feature_steps(features/step_definitions/step_definitions)
endif(CUKE_FOUND)

if(STEP_SOURCES)
    # Find all feature files
    FILE(GLOB_RECURSE FEATURE_FILES features *.feature)

    source_group("Feature Files" FILES ${FEATURE_FILES})

    add_executable(cucumber-cpp_wireserver
            ${STEP_SOURCES}
            ${FEATURE_FILES}
            )
    add_executable(feature::wireserver ALIAS cucumber-cpp_wireserver)

    set_target_properties(cucumber-cpp_wireserver
            PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${TEST_RUNTIME_OUTPUT_DIRECTORY}"
            )

    #
    # Boost
    #
    if(USE_STATIC_BOOST)
        set(Boost_USE_STATIC_LIBS ON)
    else(USE_STATIC_BOOST)
        target_compile_definitions(cucumber-cpp_wireserver
                PRIVATE
                BOOST_ALL_DYN_LINK
                )
    endif(USE_STATIC_BOOST)

    set(CORE_BOOST_LIBS thread system regex date_time program_options filesystem)

    find_package(Boost COMPONENTS ${CORE_BOOST_LIBS} REQUIRED)

    target_include_directories(cucumber-cpp_wireserver
            SYSTEM
            PRIVATE
            ${Boost_INCLUDE_DIRS}
            )

    target_link_libraries(cucumber-cpp_wireserver
            Cuke::Cucumber-cpp
            ${Boost_LIBRARIES}
            )

    if(CMAKE_COMPILER_IS_CLANGCXX)
        target_compile_options(cucumber-cpp_wireserver
                PRIVATE
                -Wno-non-virtual-dtor
                -Wno-global-constructors
                )
    endif(CMAKE_COMPILER_IS_CLANGCXX)

    #
    # Google Test driver
    #
    find_package(GTest REQUIRED)

    target_include_directories(cucumber-cpp_wireserver
            SYSTEM
            PRIVATE
            ${GTEST_INCLUDE_DIRS}
            )
    target_link_libraries(cucumber-cpp_wireserver
            ${GTEST_LIBRARIES}
            )

    if(UNIX)
        find_package(Threads) # GTest needs this and it's a static library
        target_link_libraries(cucumber-cpp_wireserver
                ${CMAKE_THREAD_LIBS_INIT}
                )
    endif(UNIX)

    if(WIN32)
        target_link_libraries(cucumber-cpp_wireserver
                ws2_32
                )
    endif(WIN32)


    ###############################
    # Installing gem dependencies
    ###############################
    find_program(BUNDLE bundle)
    if(BUNDLE)
        message(STATUS "Installing gem dependencies")
        execute_process(COMMAND ${BUNDLE} WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
        execute_process(COMMAND ${BUNDLE} show cucumber WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} OUTPUT_VARIABLE CUCUMBER_PATH)
    else(BUNDLE)
        message(WARNING "Could not find Bundler: skipping Ruby Gem management")
    endif(BUNDLE)

    ##############################################
    # Create run targets if cucumber is installed
    ##############################################
    find_program(CUCUMBER_RUBY cucumber
        PATHS ${CUCUMBER_PATH})
    if(CUCUMBER_RUBY)
        message(STATUS "Found Cucumber")
        # Target: run feature tests
        # Run all features except features tagged  @wip or @proposal

        if(WIN32)
            add_custom_target(start_wireserver
                    start /B $<TARGET_FILE:cucumber-cpp_wireserver>
                    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                    COMMENT "Start wireserver."
                    )
        else(WIN32)
            add_custom_target(start_wireserver
                    feature::wireserver &
                    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                    COMMENT "Start wireserver."
                    )
        endif(WIN32)

        add_dependencies(start_wireserver
                feature::wireserver
                )

        add_custom_target(run_feature_test
                ${CUCUMBER_RUBY} -P --no-color -f pretty -s features
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                COMMENT "Running cucumber."
                )
        if(UNIX)
            add_dependencies(run_feature_test
                    start_wireserver
                    )
        endif(UNIX)
    else(CUCUMBER_RUBY)
        message(WARNING "Could not find Cucumber: Install cucumber first in order to run tests")
    endif(CUCUMBER_RUBY)
endif(STEP_SOURCES)
