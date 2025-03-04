########################################################################################################################################################
# GoogleTest Configuration
########################################################################################################################################################
# Set variables before including googletest
set(BUILD_GMOCK ON CACHE BOOL "Build GMock" FORCE)
set(INSTALL_GTEST OFF CACHE BOOL "Don't install gtest" FORCE)
set(gtest_force_shared_crt ON CACHE BOOL "Use shared CRT" FORCE)
set(gtest_disable_pthreads OFF CACHE BOOL "Don't disable pthreads" FORCE)

# Add compile definitions for GoogleTest to match PyTorch ABI
set(CMAKE_CXX_FLAGS_OLD ${CMAKE_CXX_FLAGS})
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_GLIBCXX_USE_CXX11_ABI=0")

# Add the GoogleTest subdirectory
add_subdirectory(csrc/third_party/googletest)

# Restore original flags
set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS_OLD})

# Create aliases that behave more predictably
if(NOT TARGET GTest::GTest)
    add_library(GTest::GTest ALIAS gtest)
    add_library(GTest::Main ALIAS gtest_main)
    add_library(GMock::GMock ALIAS gmock)
    add_library(GMock::Main ALIAS gmock_main)
endif()

# Print information about GoogleTest targets
get_target_property(GTEST_INCLUDE_DIRS gtest INTERFACE_INCLUDE_DIRECTORIES)
message(STATUS "GoogleTest include directories: ${GTEST_INCLUDE_DIRS}")
