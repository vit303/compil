#include <stdio.h>

struct Point {
    int x;
    int y;
};

__attribute__((always_inline))
int sum(struct Point p) {
    return p.x + p.y;
}

int main() {
    struct Point p = {2, 3};
    int result = sum(p);
    printf("%d\n", result);
    return 0;
}
