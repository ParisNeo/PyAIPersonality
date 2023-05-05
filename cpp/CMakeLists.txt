cmake_minimum_required(VERSION 3.12)

project(AIPersonality)

# Add executable target
add_executable(my_executable main.cpp AIPersonality.cpp)

# Find required libraries
find_package(yaml-cpp REQUIRED)
find_package(stb REQUIRED)

# Link libraries
target_link_libraries(my_executable PRIVATE yaml-cpp stb)
