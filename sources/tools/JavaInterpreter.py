import subprocess
import os, sys
import tempfile
import re

if __name__ == "__main__": # if running as a script for individual testing
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sources.tools.tools import Tools
from sources.tools.sandbox import hand_over_path, subprocess_isolation

class JavaInterpreter(Tools):
    """
    This class is a tool to allow execution of Java code.
    """
    def __init__(self):
        super().__init__()
        self.tag = "java"
        self.name = "Java Interpreter"
        self.description = "This tool allows you to execute Java code."

    def execute(self, codes: str, safety=False) -> str:
        """
        Execute Java code by compiling and running it.
        """
        output = ""
        code = '\n'.join(codes) if isinstance(codes, list) else codes

        if safety and input("Execute code? y/n ") != "y":
            return "Code rejected by user."

        with tempfile.TemporaryDirectory() as tmpdirname:
            hand_over_path(tmpdirname)
            source_file = os.path.join(tmpdirname, "Main.java")
            class_dir = tmpdirname
            with open(source_file, 'w') as f:
                f.write(code)

            try:
                isolation = subprocess_isolation(self.work_dir)
                compile_command = ["javac", "-d", class_dir, source_file]
                compile_result = subprocess.run(
                    compile_command,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    **isolation
                )

                if compile_result.returncode != 0:
                    return f"Compilation failed: {compile_result.stderr}"

                run_command = ["java", "-cp", class_dir, "Main"]
                run_result = subprocess.run(
                    run_command,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    **isolation
                )

                if run_result.returncode != 0:
                    return f"Execution failed: {run_result.stderr}"
                output = run_result.stdout

            except subprocess.TimeoutExpired as e:
                return f"Execution timed out: {str(e)}"
            except FileNotFoundError:
                return "Error: 'java' or 'javac' not found. Ensure Java is installed and in PATH."
            except Exception as e:
                return f"Code execution failed: {str(e)}"

        return output

    def interpreter_feedback(self, output: str) -> str:
        """
        Provide feedback based on the output of the code execution.
        """
        if self.execution_failure_check(output):
            feedback = f"[failure] Error in execution:\n{output}"
        else:
            feedback = "[success] Execution success, code output:\n" + output
        return feedback

    def execution_failure_check(self, feedback: str) -> bool:
        """
        Check if the code execution failed.
        """
        error_patterns = [
            r"error",
            r"failed",
            r"exception",
            r"invalid",
            r"syntax",
            r"cannot",
            r"stack trace",
            r"unresolved",
            r"not found"
        ]
        combined_pattern = "|".join(error_patterns)
        if re.search(combined_pattern, feedback, re.IGNORECASE):
            return True
        return False

if __name__ == "__main__":
    codes = [
"""
import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class Main extends JPanel {
    private double[][] vertices = {
        {-1, -1, -1}, {1, -1, -1}, {1, 1, -1}, {-1, 1, -1}, // Back face
        {-1, -1, 1}, {1, -1, 1}, {1, 1, 1}, {-1, 1, 1}      // Front face
    };
    private int[][] edges = {
        {0, 1}, {1, 2}, {2, 3}, {3, 0}, // Back face
        {4, 5}, {5, 6}, {6, 7}, {7, 4}, // Front face
        {0, 4}, {1, 5}, {2, 6}, {3, 7}  // Connecting edges
    };
    private double angleX = 0, angleY = 0;
    private final double scale = 100;
    private final double distance = 5;

    public Main() {
        Timer timer = new Timer(50, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                angleX += 0.03;
                angleY += 0.05;
                repaint();
            }
        });
        timer.start();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        g2d.setColor(Color.BLACK);
        g2d.fillRect(0, 0, getWidth(), getHeight());
        g2d.setColor(Color.WHITE);

        double[][] projected = new double[vertices.length][2];
        for (int i = 0; i < vertices.length; i++) {
            double x = vertices[i][0];
            double y = vertices[i][1];
            double z = vertices[i][2];

            // Rotate around X-axis
            double y1 = y * Math.cos(angleX) - z * Math.sin(angleX);
            double z1 = y * Math.sin(angleX) + z * Math.cos(angleX);

            // Rotate around Y-axis
            double x1 = x * Math.cos(angleY) + z1 * Math.sin(angleY);
            double z2 = -x * Math.sin(angleY) + z1 * Math.cos(angleY);

            // Perspective projection
            double factor = distance / (distance + z2);
            double px = x1 * factor * scale;
            double py = y1 * factor * scale;

            projected[i][0] = px + getWidth() / 2;
            projected[i][1] = py + getHeight() / 2;
        }

        // Draw edges
        for (int[] edge : edges) {
            int x1 = (int) projected[edge[0]][0];
            int y1 = (int) projected[edge[0]][1];
            int x2 = (int) projected[edge[1]][0];
            int y2 = (int) projected[edge[1]][1];
            g2d.drawLine(x1, y1, x2, y2);
        }
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Rotating 3D Cube");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400, 400);
        frame.add(new Main());
        frame.setVisible(true);
    }
}
"""
    ]
    j = JavaInterpreter()
    print(j.execute(codes))