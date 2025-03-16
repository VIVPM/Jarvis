#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;

    long long dp[n + 1];
    dp[0] = 0;
    if (n > 0) {
        dp[1] = 1;
    }

    long long sum = 0;
    for (int i = 2; i <= n; ++i) {
        dp[i] = dp[i - 1] + dp[i - 2];
    }

    for (int i = 0; i < n; ++i){
        if(i <= n){
            sum += dp[i];
        }
    }

    cout << sum << endl;

    return 0;
}
