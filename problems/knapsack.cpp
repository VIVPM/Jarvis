#include <iostream>
#include <vector>
using namespace std;

int knapsack(int W, vector<int> weights, vector<int> values, int n) {
    vector<int> dp(W + 1, 0);

    for (int i = 0; i < n; i++) {
        for (int w = W; w >= weights[i]; w--) {
            dp[w] = max(dp[w], values[i] + dp[w - weights[i]]);
        }
    }
    return dp[W];
}

int main() {
    int n, W;

    cout << "Enter the number of items: ";
    cin >> n;

    vector<int> values(n);
    vector<int> weights(n);

    cout << "Enter the values of the items: ";
    for (int i = 0; i < n; i++) {
        cin >> values[i];
    }

    cout << "Enter the weights of the items: ";
    for (int i = 0; i < n; i++) {
        cin >> weights[i];
    }

    cout << "Enter the knapsack capacity: ";
    cin >> W;

    cout << "Maximum value: " << knapsack(W, weights, values, n) << endl;

    return 0;
}
