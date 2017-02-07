#include <gtest/gtest.h>
#include <cucumber-cpp/autodetect.hpp>

namespace
{

using cucumber::ScenarioScope;

struct Context {
    int number_1{};
    int number_2{};
    int result{};
};

GIVEN("^the numbers (-?\\d+) and (-?\\d+)$") {
    REGEX_PARAM(int, number_1);
    REGEX_PARAM(int, number_2);
    ScenarioScope<Context> context;
    context->number_1 = number_1;
    context->number_2 = number_2;
}

WHEN("^this numbers are multiplied$") {
    ScenarioScope<Context> context;
    context->result = context->number_1 * context->number_2;
}

THEN("^the result should be (-?\\d+)$") {
    REGEX_PARAM(int, result);
    ScenarioScope<Context> context;
    ASSERT_EQ(result , context->result);
}

}//namespace
