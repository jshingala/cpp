#include <bits/stdc++.h>
using namespace std;

int toMinutes(const string& hhmm) { return stoi(hhmm.substr(0, 2)) * 60 + stoi(hhmm.substr(3, 2)); }
string hhmm(int m) { char b[16]; snprintf(b, sizeof b, "%02d:%02d", m / 60, m % 60); return b; }
string nextDate(const string& d) {                            // "YYYY-MM-DD" plus one day
    int y = stoi(d.substr(0, 4)), m = stoi(d.substr(5, 2)), day = stoi(d.substr(8, 2));
    static const int len[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    bool leap = (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
    if (++day > len[m - 1] + (m == 2 && leap)) { day = 1; if (++m > 12) { m = 1; y++; } }
    char b[40]; snprintf(b, sizeof b, "%04d-%02d-%02d", y, m, day);
    return b;
}

string solve(istream& in) {
    string bsText, beText, line;
    int n;
    in >> bsText >> beText >> n;
    getline(in, line);                                       // finish the count line
    int bs = toMinutes(bsText), be = toMinutes(beText);
    map<pair<long long, string>, vector<pair<int, int>>> busy;   // (employee, date) -> busy [start, end) in business hours
    for (int r = 0; r < n && getline(in, line);) {
        if (line.find_first_not_of(" \t\r") == string::npos) continue;   // skip blank lines
        r++;
        stringstream ss(line);
        string emp, meeting, join, leave;
        getline(ss, emp, ','); getline(ss, meeting, ','); getline(ss, join, ','); getline(ss, leave, ',');
        long long e = stoll(emp);
        string jd = join.substr(0, 10), ld = leave.substr(0, 10);
        int jm = toMinutes(join.substr(11, 5)), lm = toMinutes(leave.substr(11, 5));
        busy[{e, jd}];                                       // the record's join date always counts
        for (string d = jd; d <= ld; d = nextDate(d)) {      // split a meeting that crosses midnight
            int s = d == jd ? jm : 0, t = d == ld ? lm : 24 * 60;
            if (s >= t) continue;                            // nothing of this meeting on date d
            auto& v = busy[{e, d}];
            int cs = max(s, bs), ct = min(t, be);            // keep only the part inside business hours
            if (cs < ct) v.push_back({cs, ct});
        }
    }
    string out;
    for (auto& [key, v] : busy) {
        sort(v.begin(), v.end());
        int bestStart = bs, bestLen = 0, cursor = bs;        // cursor = end of the busy time merged so far
        auto consider = [&](int s, int t) {                  // '>' keeps the earliest of tied gaps
            if (t - s > bestLen) { bestLen = t - s; bestStart = s; }
        };
        for (auto [s, t] : v) {
            if (s > cursor) consider(cursor, s);             // free gap before this meeting
            cursor = max(cursor, t);                         // overlapping or adjacent meetings merge
        }
        if (be > cursor) consider(cursor, be);
        out += to_string(key.first) + "," + key.second + "," + hhmm(bestStart) + "," +
               hhmm(bestStart + bestLen) + "," + to_string(bestLen) + "\n";
    }
    return out;
}

int main() { cout << solve(cin); }
