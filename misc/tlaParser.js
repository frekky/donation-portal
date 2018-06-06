const fs = require('fs');

module.exports = function parseTLAs(tlafile) {
  console.log("Loading TLAs from '" + tlafile + "'...");
  var tlas = [];
  try {
    var tlalines = fs.readFileSync(tlafile, "utf8").split("\n");
    for (var i = 0; i < tlalines.length; i++) {
      /* comments start with 3 spaces, don't ask me why... */
      if (tlalines[i].startsWith("   ", 0) || tlalines[i].length < 3) {
        continue;
      }
      var s = tlalines[i].split(/ _:_ /, 2);

      var n;
      if (s[1].includes("\b")) {
        // split name by backspace character and fix nastiness
        n = s[1].replace(/.[\b]/, "|").trim().replace(/^\|/, "").trim().split("|", 2);
    
        if (n[0] == "" || n[1] == "" || n.length < 2) {
          // backspace character is at start or end, try splitting by space
          n = s[1].split(" "); // try splitting by space
        }
      } else { // No backspaces, split by space.
        n = s[1].split(" ");
      }

      // TLAs are stored in a terrible format, so I might have to guess that people typically only have one first name.
      if (n.length > 2) {
        n = [n[0], n.slice(1).join(" ") ];
      } else if (n.length != 2) {
        // last resort, pretend we only got first name (probably for something like [TLA] ???????)
        n = [n[0], "??????????"];
      }
      
      var tla = {
        firstname: n[0].trim(),
        lastname: n[1],
        tla: s[0]
      };
      tlas.push(tla);
      console.log(tla.firstname + " / " + tla.lastname + " / " + tla.tla);
      // process.stdout.write("[" + s[0] + "] " + ((tlas.length % 16 == 0) ? "\n" : ""));
    }
    // process.stdout.write("\n");
  } catch (err) {
    console.warn("Error parsing TLA data!");
    console.warn(err);
    process.exit(1);
  }

  console.log('Finished parsing TLAs, got ' + tlas.length + ' different TLAs.');
  return tlas;
}